import os
import requests
from datetime import datetime, timedelta
from collections import defaultdict
import dotenv

dotenv.load_dotenv()

def get_github_stats(username, token):
    # Set GitHub API request headers
    headers = {
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github.v3+json'
    }
    
    # Get all repositories of the user
    repos_url = f'https://api.github.com/users/{username}/repos'
    repos = requests.get(repos_url, headers=headers).json()
    
    # Get yesterday's date
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    
    # Count commits from yesterday
    daily_commits = 0
    
    # Count commits for each week of each year
    weekly_commits = defaultdict(lambda: defaultdict(int))
    
    for repo in repos:
        repo_name = repo['name']
        
        # Get commit history
        commits_url = f'https://api.github.com/repos/{username}/{repo_name}/commits'
        commits = requests.get(commits_url, headers=headers).json()
        
        for commit in commits:
            try:
                commit_date = commit['commit']['author']['date'][:10]
                commit_datetime = datetime.strptime(commit_date, '%Y-%m-%d')
                
                # Check if commit is from yesterday
                if commit_date == yesterday:
                    daily_commits += 1
                
                # Count weekly commits
                year = commit_datetime.year
                week = commit_datetime.isocalendar()[1]
                weekly_commits[year][week] += 1
            except:
                continue
    
    return daily_commits, weekly_commits

def save_stats(daily_commits, weekly_commits):
    # Save statistics results
    with open('github_commit_count.md', 'w', encoding='utf-8') as f:
        # Title
        f.write('# GitHub 提交统计 / GitHub Commit Statistics\n\n')
        
        # Daily statistics
        f.write('## 最近一天统计 / Last Day Statistics\n\n')
        f.write(f'最近一天的提交数 / Commits in the last day: {daily_commits}\n\n')
        
        # Weekly statistics
        f.write('## 每年每周提交统计 / Annual Weekly Commit Statistics\n\n')
        
        for year in sorted(weekly_commits.keys()):
            f.write(f'### {year}年 / Year {year}\n\n')
            f.write('| 周数 / Week | 提交数 / Commits |\n')
            f.write('|-------------|------------------|\n')
            for week in sorted(weekly_commits[year].keys()):
                f.write(f'| {week} | {weekly_commits[year][week]} |\n')
            f.write('\n')

def main():
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        print("Note: Install python-dotenv to support reading configuration from .env file")
        
    username = os.environ.get('GITHUB_USERNAME')
    token = os.environ.get('GITHUB_TOKEN')
    
    if not username or not token:
        raise ValueError("Please set GITHUB_USERNAME and GITHUB_TOKEN environment variables")
    
    daily_commits, weekly_commits = get_github_stats(username, token)
    save_stats(daily_commits, weekly_commits)

if __name__ == '__main__':
    main()