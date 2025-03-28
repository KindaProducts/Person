"""
Script to test the database models.

This script creates some sample data to test the models
and their relationships.
"""

from app import app, db, User, Conversation, Feedback
import config

def test_models():
    """Test the database models by creating sample data."""
    print("Testing database models...")
    
    # Use application context
    with app.app_context():
        # Clear existing data (be careful in production!)
        print("Clearing existing data...")
        Feedback.query.delete()
        Conversation.query.delete()
        User.query.delete()
        db.session.commit()
        
        # Create a test user
        print("Creating test user...")
        test_user = User(email="test@example.com", password="password123")
        db.session.add(test_user)
        db.session.commit()
        
        # Verify user was created
        user = User.query.filter_by(email="test@example.com").first()
        if user:
            print(f"✓ User created with ID: {user.id}")
            print(f"✓ Password verification works: {user.verify_password('password123')}")
        else:
            print("✗ Failed to create user")
            return
        
        # Create a test conversation
        print("\nCreating test conversation...")
        test_conversation = Conversation(
            user_id=user.id,
            user_input="Hello, I'm testing the database models.",
            ai_response="That's great! Testing is important."
        )
        db.session.add(test_conversation)
        db.session.commit()
        
        # Verify conversation was created
        conversation = Conversation.query.filter_by(user_id=user.id).first()
        if conversation:
            print(f"✓ Conversation created with ID: {conversation.id}")
            print(f"✓ User input: {conversation.user_input}")
            print(f"✓ AI response: {conversation.ai_response}")
            print(f"✓ Timestamp: {conversation.timestamp}")
        else:
            print("✗ Failed to create conversation")
            return
        
        # Create a test feedback
        print("\nCreating test feedback...")
        test_feedback = Feedback(
            conversation_id=conversation.id,
            feedback_text="Good conversation, but try to ask more questions."
        )
        db.session.add(test_feedback)
        db.session.commit()
        
        # Verify feedback was created
        feedback = Feedback.query.filter_by(conversation_id=conversation.id).first()
        if feedback:
            print(f"✓ Feedback created with ID: {feedback.id}")
            print(f"✓ Feedback text: {feedback.feedback_text}")
        else:
            print("✗ Failed to create feedback")
            return
        
        # Test relationships
        print("\nTesting relationships...")
        print(f"✓ User has {len(user.conversations)} conversation(s)")
        print(f"✓ Conversation has {len(conversation.feedbacks)} feedback(s)")
        print(f"✓ Conversation belongs to user with email: {conversation.user.email}")
        print(f"✓ Feedback belongs to conversation with ID: {feedback.conversation.id}")
        
        print("\nAll tests passed!")

if __name__ == "__main__":
    test_models() 