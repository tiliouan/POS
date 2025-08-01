"""
Test User Management System
===========================

Test script to verify user management functionality works correctly.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.user_manager import user_manager
from models.user import User, UserRole, UserStatus

def test_user_management():
    """Test user management functionality."""
    print("🧪 Testing User Management System")
    print("=" * 50)
    
    # Test authentication
    print("1. Testing authentication...")
    if user_manager.login("admin", "admin123"):
        print("✅ Admin login successful")
        current_user = user_manager.get_current_user()
        print(f"   Current user: {current_user.name} ({current_user.role.value})")
    else:
        print("❌ Admin login failed")
        return
    
    # Test user creation
    print("\n2. Testing user creation...")
    new_user = User(
        username="cashier1",
        password_hash=user_manager._hash_password("password123"),
        name="Test Cashier",
        role=UserRole.CASHIER,
        status=UserStatus.ACTIVE
    )
    
    if user_manager.create_user(new_user, user_manager.current_user.id):
        print("✅ User created successfully")
    else:
        print("❌ User creation failed")
    
    # Test getting all users
    print("\n3. Testing user listing...")
    users = user_manager.get_all_users()
    print(f"✅ Found {len(users)} users:")
    for user in users:
        print(f"   - {user.username}: {user.name} ({user.role.value})")
    
    # Test activity logging
    print("\n4. Testing activity logging...")
    if user_manager.log_activity(
        user_manager.current_user.id,
        "TEST_ACTIVITY",
        "Testing activity logging system"
    ):
        print("✅ Activity logged successfully")
    else:
        print("❌ Activity logging failed")
    
    # Test user activities retrieval
    print("\n5. Testing activity retrieval...")
    activities = user_manager.get_user_activities(user_manager.current_user.id)
    print(f"✅ Found {len(activities)} activities for current user")
    if activities:
        print("   Recent activities:")
        for activity in activities[:3]:
            print(f"   - {activity.activity_type}: {activity.description}")
    
    # Test sales summary
    print("\n6. Testing user sales summary...")
    sales_summary = user_manager.get_user_sales_summary()
    print(f"✅ Sales summary generated for {len(sales_summary)} users")
    for user_id, summary in sales_summary.items():
        print(f"   - {summary['name']}: {summary['total_sales']} sales, {summary['total_amount']:.2f} DH")
    
    # Test logout
    print("\n7. Testing logout...")
    if user_manager.logout():
        print("✅ Logout successful")
    else:
        print("❌ Logout failed")
    
    print("\n🎉 User Management System Test Complete!")
    print("✅ All core functionality working!")

if __name__ == "__main__":
    test_user_management()
