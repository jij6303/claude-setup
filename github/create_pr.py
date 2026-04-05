"""
PR 생성 스크립트

단독 실행:
    python create_pr.py --title "PR 제목" --head feature/my-branch
    python create_pr.py --title "PR 제목" --head feature/my-branch --base develop --body "설명"

모듈 사용:
    from github.create_pr import create_pr
    pr_number = create_pr(token, owner, repo, title, head, base, body)
"""
import argparse

import requests

from auth import get_token_and_config, make_headers


def create_pr(token, owner, repo, title, head, base="main", body=""):
    url = f"https://api.github.com/repos/{owner}/{repo}/pulls"
    res = requests.post(
        url,
        headers=make_headers(token),
        json={"title": title, "body": body, "head": head, "base": base},
    )
    res.raise_for_status()
    pr = res.json()
    print(f"PR 생성 완료: #{pr['number']} {pr['title']}")
    print(f"URL: {pr['html_url']}")
    return pr["number"]


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="GitHub PR 생성")
    parser.add_argument("--title", required=True, help="PR 제목")
    parser.add_argument("--head", required=True, help="소스 브랜치 (변경사항이 있는 브랜치)")
    parser.add_argument("--base", default="main", help="대상 브랜치 (기본값: main)")
    parser.add_argument("--body", default="", help="PR 본문")
    args = parser.parse_args()

    token, config = get_token_and_config()
    create_pr(token, config["owner"], config["repo"], args.title, args.head, args.base, args.body)
