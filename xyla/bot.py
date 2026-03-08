import os
import time
from supabase import create_client, Client
from apify_client import ApifyClient

# ─── 1. SETUP ───
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://hnqpmftzwttcbvwgswmp.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "sb_publishable_Wv2u3WllKwhgn2JNXZd2nQ_gNxCKmsK")
APIFY_TOKEN = os.getenv("APIFY_TOKEN", "apify_api_LVewkbYZ6Ebm1mSzck8XAPegmoG21E4zhBu4")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
apify = ApifyClient(APIFY_TOKEN)


# ─── 2. SCRAPE VIEWS FROM APIFY ───
def update_stats():
    """Fetch all clips, scrape views via Apify, and sync back to Supabase."""
    print("Fetching active campaigns...")
    active_campaigns = supabase.table("campaigns").select("id", "name").eq("is_active", True).execute().data
    if not active_campaigns:
        print("No active campaigns to sync.")
        return
        
    active_ids = [c["id"] for c in active_campaigns]
    active_names = [c["name"] for c in active_campaigns]

    res = supabase.table("clips_track").select("*").execute()
    all_clips = res.data

    if not all_clips:
        print("No clips found in database.")
        return

    # Sync ALL clips (not just those linked to active campaigns)
    # This ensures clips with null campaign_id also get their views updated
    clips = all_clips

    if not clips:
        print("No clips found for active campaigns.")
        return

    # Filter unique URLs by platform — strip UTM/query params first
    def clean_url(url):
        return url.split("?")[0].rstrip("/") if url else ""

    def to_reel_url(url):
        """Convert /p/ Instagram URLs to /reel/ so Apify doesn't get restricted."""
        return url.replace("/instagram.com/p/", "/instagram.com/reel/") \
                  .replace("instagram.com/p/", "instagram.com/reel/")

    tt_links = list(set([clean_url(c["video_url"]) for c in clips if "tiktok.com" in c.get("video_url", "")]))
    ig_links = list(set([
        to_reel_url(clean_url(c["video_url"]))
        for c in clips if "instagram.com" in c.get("video_url", "")
    ]))

    # TikTok Scraper
    if tt_links:
        try:
            print(f"Scraping {len(tt_links)} TikTok links...")
            run = apify.actor("clockworks/tiktok-scraper").call(run_input={"postURLs": tt_links})
            sync_to_supabase(run["defaultDatasetId"], "webVideoUrl")
        except Exception as e:
            print(f"TikTok Error: {e}")

    # Instagram Scraper (all URLs normalized to /reel/ format to bypass restrictions)
    if ig_links:
        try:
            print(f"Scraping {len(ig_links)} Instagram links: {ig_links}")
            run_input = {
                "directUrls": ig_links,
                "resultsType": "details",
                "searchLimit": 1,
                "proxy": {
                    "useApifyProxy": True,
                    "apifyProxyGroups": ["RESIDENTIAL"],
                },
                "maxConcurrency": 1,
                "maxRequestRetries": 5
            }
            run = apify.actor("apify/instagram-scraper").call(run_input=run_input)
            sync_to_supabase(run["defaultDatasetId"], "url")
        except Exception as e:
            print(f"Instagram Error: {e}")

    # After syncing views, recalculate budgets
    recalculate_budgets()
    print("[OK] Full sync complete.")


def sync_to_supabase(dataset_id, url_field):
    """Push scraped view/like counts from Apify back to clips_track."""
    items = apify.dataset(dataset_id).list_items().items
    print(f"Processing {len(items)} items from Apify...")

    for item in items:
        raw_url = item.get(url_field)
        if not raw_url:
            continue
        # Strip www + query params for consistent matching
        clean_url = raw_url.replace("www.", "").split("?")[0].rstrip("/")

        # Extract just the post shortcode (last path segment e.g. DVCLKa-D2b0)
        # This matches regardless of /p/ vs /reel/ prefix that Apify may normalize
        try:
            from urllib.parse import urlparse
            path_parts = [p for p in urlparse(clean_url).path.split("/") if p]
            shortcode = path_parts[-1] if path_parts else clean_url
        except Exception:
            shortcode = clean_url

        # Prioritize videoPlayCount (Reel grid views) over videoViewCount (unique/legacy views)
        views = item.get("videoPlayCount") or item.get("playCount") or item.get("videoViewCount") or item.get("viewCount") or 0
        likes = item.get("likesCount") or item.get("diggCount") or item.get("likeCount") or 0
        comments = item.get("commentCount") or item.get("commentsCount") or 0

        print(f"Found Data -> shortcode: {shortcode} | Views: {views} | Likes: {likes}")

        # If Apify returned 0 (Instagram rate-limited), check existing DB value
        # and skip overwriting if current value is already non-zero
        if views == 0:
            existing = supabase.table("clips_track").select("views").ilike("video_url", f"%{shortcode}%").execute()
            existing_views = existing.data[0].get("views", 0) if existing.data else 0
            if existing_views > 0:
                print(f"[SKIP] Apify returned 0 — keeping existing {existing_views:,} views for {shortcode}")
                continue

        # Match by shortcode — works for both /p/ posts and /reel/ reels
        result = supabase.table("clips_track").update({
            "views": views,
            "likes": likes,
            "comments": comments,
        }).ilike("video_url", f"%{shortcode}%").execute()

        if result.data:
            print(f"[OK] DATABASE UPDATED: {shortcode} -> {views:,} views")
        else:
            print(f"[MISS] MATCH FAILED: {clean_url} not found in your Supabase table.")

    print("Sync process finished.")


# ─── 3. BUDGET CALCULATION ENGINE ───
def recalculate_budgets():
    """
    For each campaign, calculate:
      Budget Used     = (Total Views / 1000) × CPM
      Percentage Used = (Budget Used / Total Budget) × 100
    Then update the campaigns table.
    """
    print("\n--- RECALCULATING BUDGETS ---")
    campaigns = supabase.table("campaigns").select("*").execute().data

    if not campaigns:
        print("No campaigns found in database.")
        return

    for camp in campaigns:
        camp_id = camp["id"]
        camp_name = camp.get("name", "Unknown")
        cpm_rate = float(camp.get("cpm_rate", 0))
        total_budget = float(camp.get("total_budget", 0))

        # Sum all views for APPROVED clips linked to this campaign (by campaign_id only)
        res = supabase.table("clips_track").select("views").eq("campaign_id", camp_id).eq("status", "Approved").execute()
        all_clips = res.data or []
        total_views = sum(c.get("views", 0) for c in all_clips)

        # Budget Used = (Total Views / 1000) × CPM
        calculated_budget = (total_views / 1000) * cpm_rate

        # Percentage Used = Continuous up to 100
        if total_budget > 0:
            pct_used = min((calculated_budget / total_budget) * 100, 100)
            # Payout Freeze at 95%
            budget_used = min(calculated_budget, total_budget * 0.95)

            # Auto-pause when 100% capacity is hit
            if pct_used >= 100.0:
                print(f"  [AUTO-PAUSE] {camp_name} has reached 100% capacity!")
                supabase.table("campaigns").update({
                    "is_active": False
                }).eq("id", camp_id).execute()
        else:
            pct_used = 0
            budget_used = calculated_budget

        # Update the campaigns table
        supabase.table("campaigns").update({
            "total_views": total_views,
            "budget_used": round(budget_used, 2),
            "pct_used": round(pct_used, 2),
        }).eq("id", camp_id).execute()

        print(f"  {camp_name}: {total_views:,} views | ${budget_used:,.2f} used | {pct_used:.1f}%")

    print("--- BUDGET RECALC COMPLETE ---\n")

# ─── 4. RUN ───
if __name__ == "__main__":
    print("Starting Xyla Bot Sync Service...")
    try:
        update_stats()
    except Exception as e:
        print(f"Error during sync: {e}")
    print("Sync complete. Exiting.")
