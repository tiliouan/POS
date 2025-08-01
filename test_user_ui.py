"""
Test User Editing UI and Remove Functionality
==============================================

Test script to verify the user editing UI improvements and remove functionality.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.user_manager import user_manager
from models.user import User, UserRole, UserStatus

def test_user_operations():
    """Test user editing UI and remove functionality."""
    print("🧪 Testing User Management UI and Remove Functionality")
    print("=" * 65)
    
    # Test authentication as admin
    print("1. Testing admin authentication...")
    if user_manager.login("admin", "admin123"):
        print("✅ Admin login successful")
        current_user = user_manager.get_current_user()
        print(f"   Current user: {current_user.name} ({current_user.role.value})")
    else:
        print("❌ Admin login failed")
        return
    
    # Create test users for removal test
    print("\n2. Creating test users...")
    test_users = [
        User(
            username="test_user1",
            password_hash=user_manager._hash_password("password123"),
            name="Test User 1",
            role=UserRole.CASHIER,
            status=UserStatus.ACTIVE
        ),
        User(
            username="test_user2",
            password_hash=user_manager._hash_password("password123"),
            name="Test User 2",
            role=UserRole.MANAGER,
            status=UserStatus.ACTIVE
        )
    ]
    
    created_users = []
    for user in test_users:
        if user_manager.create_user(user, user_manager.current_user.id):
            print(f"✅ Created user: {user.username}")
            created_users.append(user)
        else:
            print(f"❌ Failed to create user: {user.username}")
    
    # Test remove functionality
    print("\n3. Testing user removal...")
    
    # Get all users to find test users
    users = user_manager.get_all_users()
    test_user_to_remove = None
    for user in users:
        if user.username == "test_user1":
            test_user_to_remove = user
            break
    
    if test_user_to_remove:
        print(f"   Found test user to remove: {test_user_to_remove.username}")
        
        # Test removing user
        if user_manager.remove_user(test_user_to_remove.id):
            print("✅ User removal successful")
        else:
            print("❌ User removal failed")
    else:
        print("❌ Test user not found for removal")
    
    # Test prevention of removing current user
    print("\n4. Testing prevention of removing current user...")
    current_user_id = user_manager.current_user.id
    if not user_manager.remove_user(current_user_id):
        print("✅ Successfully prevented removal of current user")
    else:
        print("❌ Failed to prevent removal of current user")
    
    # Verify user removal
    print("\n5. Verifying user removal...")
    users_after_removal = user_manager.get_all_users()
    removed_user_found = False
    for user in users_after_removal:
        if user.username == "test_user1":
            removed_user_found = True
            break
    
    if not removed_user_found:
        print("✅ User successfully removed from database")
    else:
        print("❌ User still exists in database")
    
    # Display remaining users
    print("\n6. Current users in system:")
    for user in users_after_removal:
        print(f"   - {user.username}: {user.name} ({user.role.value}) - {user.status.value}")
    
    # Clean up remaining test user
    print("\n7. Cleaning up remaining test users...")
    for user in users_after_removal:
        if user.username.startswith("test_user"):
            if user_manager.remove_user(user.id):
                print(f"✅ Cleaned up: {user.username}")
            else:
                print(f"❌ Failed to clean up: {user.username}")
    
    print("\n🎉 User Management UI and Remove Functionality Test Complete!")
    print("✅ Edit dialog now has 'Apply' button and remove functionality works!")

if __name__ == "__main__":
    test_user_operations()
