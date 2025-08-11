"""
API v1 Router
"""

from fastapi import APIRouter

from app.api.api_v1.endpoints import products, sites, alerts, jobs, auth, users, site_wizard, user_preferences, orders, orders_stream

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(sites.router, prefix="/sites", tags=["sites"])
api_router.include_router(site_wizard.router, prefix="/site-wizard", tags=["site-wizard"])
api_router.include_router(products.router, prefix="/products", tags=["products"])
api_router.include_router(alerts.router, prefix="/alerts", tags=["alerts"])
api_router.include_router(jobs.router, prefix="/jobs", tags=["scraping-jobs"])
api_router.include_router(user_preferences.router, prefix="/user-preferences", tags=["user-preferences"])
api_router.include_router(orders.router, prefix="/orders", tags=["orders"])
api_router.include_router(orders_stream.router, prefix="/orders", tags=["orders-stream"]) 
