from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, get_db, Base
from models import User, Building, Permit, Approval, Inspection, Hazard, Demolition, AuditLog, UserRole, PermitStatus, HazardStatus, HazardLevel
from auth import hash_password
from routers.auth_router import router as auth_router
from routers.building_router import router as building_router
from routers.permit_router import router as permit_router
from routers.inspection_router import router as inspection_router
from routers.hazard_router import router as hazard_router
from routers.demolition_router import router as demolition_router
from routers.audit_router import router as audit_router
from routers.user_router import router as user_router

Base.metadata.create_all(bind=engine)


def seed_data():
    db = next(get_db())
    if db.query(User).first():
        return
    users = [
        User(username="constructor1", password_hash=hash_password("123456"), real_name="张建国", role=UserRole.constructor.value, org_name="古建修缮工程公司", phone="13800138001"),
        User(username="constructor2", password_hash=hash_password("123456"), real_name="李修远", role=UserRole.constructor.value, org_name="文保施工队", phone="13800138002"),
        User(username="inspector1", password_hash=hash_password("123456"), real_name="王巡检", role=UserRole.inspector.value, org_name="市文物局", phone="13900139001"),
        User(username="inspector2", password_hash=hash_password("123456"), real_name="赵巡查", role=UserRole.inspector.value, org_name="区安监站", phone="13900139002"),
        User(username="heritage1", password_hash=hash_password("123456"), real_name="陈文保", role=UserRole.heritage.value, org_name="市文物局", phone="13700137001"),
        User(username="safety1", password_hash=hash_password("123456"), real_name="刘安监", role=UserRole.safety.value, org_name="区安监站", phone="13700137002"),
    ]
    db.add_all(users)
    buildings = [
        Building(name="文峰塔", address="南城区文峰路1号", heritage_level="国家级", description="明代砖塔，七层八角"),
        Building(name="城隍庙大殿", address="东城区城隍庙街12号", heritage_level="省级", description="清代木构大殿，面阔五间"),
        Building(name="钟鼓楼", address="中心区鼓楼广场", heritage_level="市级", description="明代砖木结构楼阁"),
        Building(name="古戏台", address="西城区戏台巷8号", heritage_level="市级", description="清代戏台，歇山顶"),
    ]
    db.add_all(buildings)
    db.commit()


@asynccontextmanager
async def lifespan(app):
    seed_data()
    yield


app = FastAPI(title="古建筑修缮脚手架许可与巡检系统", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(building_router)
app.include_router(permit_router)
app.include_router(inspection_router)
app.include_router(hazard_router)
app.include_router(demolition_router)
app.include_router(audit_router)
app.include_router(user_router)


@app.get("/api/health")
def health():
    return {"status": "ok"}
