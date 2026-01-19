async def fetch_commits(
     repo_name: str,
     target_date: date,
    access_token: str
) -> list[dict]:
    """
    특정 날짜의 커밋 목록 수집
    R-BIZ-3: UTC 00:00:00 ~ 23:59:59 범위 검색
    """
    logger.info(f"Fetching commits for repository: {repo_name}, date: {target_date}")

    async with httpx.AsyncClient() as client:
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/vnd.github.v3+json",
        }
        # 날짜 범위 설정 (UTC 기준)
        since = datetime.combine(target_date, time.min).isoformat() + "Z"
        until = datetime.combine(target_date, time.max).isoformat() + "Z"
        params = {
            "since": since,
            "until": until,
            "per_page": 100 # 하루 커밋이 100개 넘는 경우는 드물므로 MVP 적합
        }
        url = f"https://api.github.com/repos/{repo_name}/commits"
        try:
            response = await client.get(url, headers=headers, params=params)
            response.raise_for_status()
            commits = response.json()
            logger.info(f"Found {len(commits)} commits for {repo_name}")
            return commits
        except httpx.HTTPStatusError as e:
            logger.error(f"GitHub API Error fetching commits: {e.response.text}")
            _handle_github_error(e)
        except httpx.RequestError as e:
            logger.error(f"Network error fetching commits: {e}")
            raise GithubApiError(message=f"Network error: {str(e)}")