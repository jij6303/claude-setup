"""
파일 삭제 커밋 스크립트

단독 실행:
    python delete_file.py --file path/to/file.py --branch feature/my-branch
    python delete_file.py --file path/to/file.py --branch feature/my-branch --message "remove: 파일 삭제"

모듈 사용:
    from github.delete_file import delete_file
    delete_file(token, owner, repo, branch_name, file_path, commit_message)
"""
import argparse

import requests

from auth import get_token_and_config, make_headers


def delete_file(token, owner, repo, branch_name, file_path, commit_message=None):
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{file_path}"

    res = requests.get(url, headers=make_headers(token), params={"ref": branch_name})
    res.raise_for_status()
    file_sha = res.json()["sha"]

    if commit_message is None:
        commit_message = f"remove: {file_path} 삭제"

    res = requests.delete(
        url,
        headers=make_headers(token),
        json={"message": commit_message, "sha": file_sha, "branch": branch_name},
    )
    res.raise_for_status()
    commit = res.json()["commit"]
    print(f"파일 삭제 커밋 완료: {commit['sha'][:7]} - {commit['message']}")
    return commit["sha"]


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="GitHub 파일 삭제 커밋")
    parser.add_argument("--file", required=True, help="삭제할 파일 경로 (레포 기준)")
    parser.add_argument("--branch", required=True, help="대상 브랜치")
    parser.add_argument("--message", default=None, help="커밋 메시지 (기본값: 자동 생성)")
    args = parser.parse_args()

    token, config = get_token_and_config()
    delete_file(token, config["owner"], config["repo"], args.branch, args.file, args.message)
