import json
import time
import base64
import requests
import jwt  # PyJWT


def load_config(path="github_bot.json"):
    with open(path) as f:
        return json.load(f)


def generate_jwt(app_id, private_key_path):
    with open(private_key_path, "r") as f:
        private_key = f.read()
    now = int(time.time())
    payload = {"iat": now - 60, "exp": now + 600, "iss": str(app_id)}
    return jwt.encode(payload, private_key, algorithm="RS256")


def get_installation_token(jwt_token, installation_id):
    url = f"https://api.github.com/app/installations/{installation_id}/access_tokens"
    headers = {
        "Authorization": f"Bearer {jwt_token}",
        "Accept": "application/vnd.github+json",
    }
    res = requests.post(url, headers=headers)
    res.raise_for_status()
    return res.json()["token"]


def make_headers(token):
    return {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
    }


# 1. 이슈 생성
def create_issue(token, owner, repo, title, body):
    url = f"https://api.github.com/repos/{owner}/{repo}/issues"
    res = requests.post(url, headers=make_headers(token), json={"title": title, "body": body})
    res.raise_for_status()
    issue = res.json()
    print(f"[1] 이슈 생성 완료: #{issue['number']} {issue['title']}")
    return issue["number"]


# 2. 브랜치 생성
def create_branch(token, owner, repo, branch_name, base_branch="main"):
    # base 브랜치의 최신 SHA 조회
    url = f"https://api.github.com/repos/{owner}/{repo}/git/ref/heads/{base_branch}"
    res = requests.get(url, headers=make_headers(token))
    res.raise_for_status()
    sha = res.json()["object"]["sha"]

    url = f"https://api.github.com/repos/{owner}/{repo}/git/refs"
    res = requests.post(
        url,
        headers=make_headers(token),
        json={"ref": f"refs/heads/{branch_name}", "sha": sha},
    )
    res.raise_for_status()
    print(f"[2] 브랜치 생성 완료: {branch_name}")
    return sha


# 3 & 4. main.py 삭제 커밋 & 푸시
def delete_file_commit(token, owner, repo, branch_name, file_path, commit_message):
    # 파일의 현재 SHA 조회 (삭제에 필요)
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{file_path}"
    res = requests.get(url, headers=make_headers(token), params={"ref": branch_name})
    res.raise_for_status()
    file_sha = res.json()["sha"]

    res = requests.delete(
        url,
        headers=make_headers(token),
        json={"message": commit_message, "sha": file_sha, "branch": branch_name},
    )
    res.raise_for_status()
    commit = res.json()["commit"]
    print(f"[3/4] 파일 삭제 커밋 완료: {commit['sha'][:7]} - {commit['message']}")


# 4. PR 생성
def create_pull_request(token, owner, repo, branch_name, base_branch, title, body, issue_number):
    url = f"https://api.github.com/repos/{owner}/{repo}/pulls"
    res = requests.post(
        url,
        headers=make_headers(token),
        json={
            "title": title,
            "body": body,
            "head": branch_name,
            "base": base_branch,
        },
    )
    res.raise_for_status()
    pr = res.json()
    print(f"[4] PR 생성 완료: #{pr['number']} {pr['title']}")
    return pr["number"]


# 5. 리뷰 요청
def request_review(token, owner, repo, pr_number, reviewers):
    url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}/requested_reviewers"
    res = requests.post(url, headers=make_headers(token), json={"reviewers": reviewers})
    res.raise_for_status()
    print(f"[5] 리뷰 요청 완료: {', '.join(reviewers)}")


def main():
    config = load_config()
    owner = config["owner"]
    repo = config["repo"]

    jwt_token = generate_jwt(config["app_id"], config["private_key_path"])
    token = get_installation_token(jwt_token, config["installation_id"])

    branch_name = "cleanup/remove-sample-main"
    base_branch = "main"

    # 1. 이슈 생성
    issue_number = create_issue(
        token, owner, repo,
        title="[Cleanup] 샘플 main.py 파일 제거",
        body="초기 PyCharm 프로젝트 생성 시 자동으로 생성된 샘플 `main.py`를 제거합니다.",
    )

    # 2. 브랜치 생성
    create_branch(token, owner, repo, branch_name, base_branch)

    # 3 & 4. main.py 삭제 커밋
    delete_file_commit(
        token, owner, repo, branch_name,
        file_path="main.py",
        commit_message=f"remove: 샘플 main.py 제거 (closes #{issue_number})",
    )

    # 4. PR 생성
    pr_number = create_pull_request(
        token, owner, repo,
        branch_name=branch_name,
        base_branch=base_branch,
        title=f"[Cleanup] 샘플 main.py 제거 (#{issue_number})",
        body=f"Closes #{issue_number}\n\n초기 PyCharm 샘플 파일인 `main.py`를 제거합니다.",
        issue_number=issue_number,
    )

    # 5. 리뷰 요청 (레포 오너)
    request_review(token, owner, repo, pr_number, reviewers=[owner])


if __name__ == "__main__":
    main()
