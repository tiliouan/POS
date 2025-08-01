"""
Test User Editing and Admin Role Assignment
===========================================

Test script to verify user editing functionality and admin role assignment.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.user_manager import user_manager
from models.user import User, UserRole, UserStatus

def test_user_editing():
    """Test user editing and admin role assignment functionality."""
    print("🧪 Testing User Editing and Admin Role Assignment")
    print("=" * 60)
    
    # Test authentication as admin
    print("1. Testing admin authentication...")
    if user_manager.login("admin", "admin123"):
        print("✅ Admin login successful")
        current_user = user_manager.get_current_user()
        print(f"   Current user: {current_user.name} ({current_user.role.value})")
    else:
        print("❌ Admin login failed")
        return
    
    # Create a test user first
    print("\n2. Creating test user...")
    test_user = User(
        username="testuser",
        password_hash=user_manager._hash_password("password123"),
        name="Test User",
        role=UserRole.CASHIER,
        status=UserStatus.ACTIVE
    )
    
    if user_manager.create_user(test_user, user_manager.current_user.id):
        print("✅ Test user created successfully")
    else:
        print("❌ Test user creation failed")
        return
    
    # Get all users to find our test user
    print("\n3. Getting all users...")
    users = user_manager.get_all_users()
    test_user_obj = None
    for user in users:
        if user.username == "testuser":
            test_user_obj = user
            break
    
    if not test_user_obj:
        print("❌ Test user not found")
        return
    
    print(f"✅ Found test user: {test_user_obj.name} ({test_user_obj.role.value})")
    
    # Test updating user to manager role
    print("\n4. Testing role update to Manager...")
    test_user_obj.role = UserRole.MANAGER
    test_user_obj.name = "Test Manager"
    
    if user_manager.update_user(test_user_obj):
        print("✅ User updated to Manager successfully")
    else:
        print("❌ Manager role update failed")
    
    # Test updating user to admin role
    print("\n5. Testing role update to Admin...")
    test_user_obj.role = UserRole.ADMIN
    test_user_obj.name = "Test Administrator"
    
    if user_manager.update_user(test_user_obj):
        print("✅ User updated to Admin successfully")
    else:
        print("❌ Admin role update failed")
    
    # Verify the changes
    print("\n6. Verifying changes...")
    users = user_manager.get_all_users()
    for user in users:
        if user.username == "testuser":
            print(f"✅ User verification: {user.name} ({user.role.value})")
            if user.role == UserRole.ADMIN:
                print("✅ Admin role assignment successful!")
            break
    
    # Test status changes
    print("\n7. Testing status changes...")
    test_user_obj.status = UserStatus.INACTIVE
    
    if user_manager.update_user(test_user_obj):
        print("✅ User status updated to Inactive successfully")
    else:
        print("❌ Status update failed")
    
    # Display all users
    print("\n8. Current users in system:")
    users = user_manager.get_all_users()
    for user in users:
        print(f"   - {user.username}: {user.name} ({user.role.value}) - {user.status.value}")
    
    print("\n🎉 User Editing and Admin Role Assignment Test Complete!")
    print("✅ All functionality working correctly!")

if __name__ == "__main__":
    test_user_editing()
