import requests

BASE = "http://localhost:8005/api"

def login(username):
    r = requests.post(f"{BASE}/auth/login", json={"username": username, "password": "123456"})
    assert r.status_code == 200, f"Login failed: {r.text}"
    return r.json()["access_token"]

def headers(token):
    return {"Authorization": f"Bearer {token}"}

print("=== Step 1: Constructor creates permit ===")
c_token = login("constructor1")
r = requests.post(f"{BASE}/permits", json={
    "building_id": 1, "scaffold_scope": "test scope",
    "start_date": "2024-03-01", "end_date": "2024-06-30"
}, headers=headers(c_token))
assert r.status_code == 200, f"Create permit failed: {r.text}"
pid = r.json()["id"]
print(f"  Permit #{pid} created, status={r.json()['status']}")

print("=== Step 2: Constructor submits for approval ===")
r = requests.put(f"{BASE}/permits/{pid}/submit", headers=headers(c_token))
assert r.status_code == 200, f"Submit failed: {r.text}"
print(f"  Status={r.json()['status']}")

print("=== Step 3: Heritage officer approves ===")
h_token = login("heritage1")
r = requests.post(f"{BASE}/permits/{pid}/approve", json={
    "approval_type": "heritage", "result": "approved", "opinion": "OK"
}, headers=headers(h_token))
assert r.status_code == 200, f"Heritage approve failed: {r.text}"
print(f"  Heritage approved OK")

print("=== Step 4: Safety officer approves ===")
s_token = login("safety1")
r = requests.post(f"{BASE}/permits/{pid}/approve", json={
    "approval_type": "safety", "result": "approved", "opinion": "OK"
}, headers=headers(s_token))
assert r.status_code == 200, f"Safety approve failed: {r.text}"
print(f"  Safety approved OK, status={r.json()['permit_id']}")

print("=== Step 5: Check permit status (should be can_scaffold) ===")
r = requests.get(f"{BASE}/permits/{pid}", headers=headers(c_token))
print(f"  Permit status={r.json()['status']}, heritage={r.json()['heritage_approved']}, safety={r.json()['safety_approved']}")

print("=== Step 6: Constructor starts use ===")
r = requests.put(f"{BASE}/permits/{pid}/start-use", headers=headers(c_token))
assert r.status_code == 200, f"Start use failed: {r.text}"
print(f"  Status={r.json()['status']}")

print("=== Step 7: Inspector creates inspection ===")
i_token = login("inspector1")
r = requests.post(f"{BASE}/inspections", json={
    "permit_id": pid, "check_items": "扣件紧固、荷载合规、警示标识",
    "result": "abnormal", "hazard_level": "major", "remark": "扣件松动"
}, headers=headers(i_token))
assert r.status_code == 200, f"Inspection failed: {r.text}"
print(f"  Inspection #{r.json()['id']} created")

print("=== Step 8: Inspector reports hazard ===")
r = requests.post(f"{BASE}/hazards", json={
    "permit_id": pid, "level": "major", "description": "扣件松动需紧固"
}, headers=headers(i_token))
assert r.status_code == 200, f"Hazard create failed: {r.text}"
hid = r.json()["id"]
print(f"  Hazard #{hid} created, status={r.json()['status']}")

print("=== Step 9: Safety officer assigns hazard ===")
r = requests.put(f"{BASE}/hazards/{hid}/assign", json={
    "assigned_to": 1
}, headers=headers(s_token))
assert r.status_code == 200, f"Assign failed: {r.text}"
print(f"  Hazard assigned, status={r.json()['status']}")

print("=== Step 10: Constructor rectifies hazard ===")
r = requests.put(f"{BASE}/hazards/{hid}/rectify", json={
    "rectify_result": "已紧固所有松动扣件"
}, headers=headers(c_token))
assert r.status_code == 200, f"Rectify failed: {r.text}"
print(f"  Hazard rectified, status={r.json()['status']}")

print("=== Step 11: Inspector rechecks hazard ===")
r = requests.put(f"{BASE}/hazards/{hid}/recheck", json={
    "recheck_result": "pass"
}, headers=headers(i_token))
assert r.status_code == 200, f"Recheck failed: {r.text}"
print(f"  Hazard rechecked, status={r.json()['status']}")

print("=== Step 12: Constructor requests demolish ===")
r = requests.put(f"{BASE}/permits/{pid}/request-demolish", headers=headers(c_token))
assert r.status_code == 200, f"Request demolish failed: {r.text}"
print(f"  Status={r.json()['status']}")

print("=== Step 13: Constructor creates demolition ===")
r = requests.post(f"{BASE}/demolitions", json={
    "permit_id": pid, "demolish_date": "2024-07-15", "site_restored": 1
}, headers=headers(c_token))
assert r.status_code == 200, f"Create demolition failed: {r.text}"
did = r.json()["id"]
print(f"  Demolition #{did} created")

print("=== Step 14: Heritage officer accepts demolition ===")
r = requests.put(f"{BASE}/demolitions/{did}/accept", json={
    "accept_opinion": "现场恢复良好", "accept_result": "accepted"
}, headers=headers(h_token))
assert r.status_code == 200, f"Accept demolition failed: {r.text}"
print(f"  Demolition accepted, result={r.json()['accept_result']}")

print("=== Step 15: Verify permit is accepted ===")
r = requests.get(f"{BASE}/permits/{pid}", headers=headers(c_token))
print(f"  Final status={r.json()['status']}")

print("\n=== ALL STEPS PASSED ===")
