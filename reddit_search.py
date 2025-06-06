import praw
import os
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Reddit API credentials
CLIENT_ID = os.getenv('REDDIT_CLIENT_ID')
CLIENT_SECRET = os.getenv('REDDIT_CLIENT_SECRET')
USER_AGENT = os.getenv('REDDIT_USER_AGENT', 'script:reddit_search:v1.0 (by /u/YourUsername)')

def setup_reddit_api():
    """Set up and return Reddit API client"""
    reddit = praw.Reddit(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        user_agent=USER_AGENT
    )
    return reddit

def get_recent_posts(keyword, days=365):
    """Fetch recent Reddit posts containing the keyword"""
    reddit = setup_reddit_api()
    
    # Calculate timestamp for posts from the last year
    since_timestamp = int((datetime.now() - timedelta(days=days)).timestamp())
    
    # Search across all subreddits
    search_results = reddit.subreddit('all').search(
        query=keyword,
        sort='relevance',
        time_filter='all'
    )
    
    return search_results

def get_comments(post):
    """Fetch all comments for a post"""
    post.comments.replace_more(limit=None)  # Replace MoreComments objects with actual comments
    comments = []
    
    for comment in post.comments.list():
        comment_data = {
            'author': str(comment.author),
            'body': comment.body,
            'created_utc': comment.created_utc,
            'score': comment.score,
            'id': comment.id,
            'parent_id': comment.parent_id,
            'is_submitter': comment.is_submitter,
            'depth': comment.depth
        }
        comments.append(comment_data)
    
    return comments

def save_posts_to_json(posts, keyword):
    """Save posts and their comments to a JSON file"""
    posts_data = []
    for post in posts:
        print(f"Fetching comments for post: {post.title}")
        comments = get_comments(post)
        print(f"Found {len(comments)} comments")
        
        post_data = {
            'title': post.title,
            'subreddit': post.subreddit.display_name,
            'author': str(post.author),
            'created_utc': post.created_utc,
            'score': post.score,
            'url': f"https://reddit.com{post.permalink}",
            'text': post.selftext,
            'num_comments': post.num_comments,
            'upvote_ratio': post.upvote_ratio,
            'comments': comments
        }
        posts_data.append(post_data)
    
    # Create filename with timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"reddit_posts_{keyword.replace(' ', '_')}_{timestamp}.json"
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(posts_data, f, indent=4, ensure_ascii=False)
    
    return filename

def main():
    keyword = "Bruvi coffee"
    print(f"Fetching Reddit posts containing '{keyword}' from the past year...")
    
    try:
        posts = get_recent_posts(keyword)
        
        found_posts = False
        posts_list = []
        for post in posts:
            found_posts = True
            posts_list.append(post)
            print("\n" + "="*80)
            print(f"Title: {post.title}")
            print(f"Subreddit: r/{post.subreddit.display_name}")
            print(f"Author: u/{post.author}")
            print(f"Posted: {datetime.fromtimestamp(post.created_utc)}")
            print(f"Score: {post.score}")
            print(f"URL: https://reddit.com{post.permalink}")
            print(f"Text: {post.selftext}")
            print("="*80)
        
        if not found_posts:
            print("No posts found matching the criteria.")
        else:
            # Save posts and comments to JSON file
            filename = save_posts_to_json(posts_list, keyword)
            print(f"\nSaved {len(posts_list)} posts and their comments to {filename}")
            
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main() 