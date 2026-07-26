import unittest

from app.api.v1.endpoints.chat import _save_session_to_store


class FakeCollection:
    def __init__(self):
        self.docs = {}

    async def replace_one(self, query, replacement, upsert=True):
        self.docs[query["_id"]] = replacement


class FakeDB:
    def __init__(self):
        self.chat_history = FakeCollection()


class ChatStorageTests(unittest.IsolatedAsyncioTestCase):
    async def test_save_session_to_store_persists_payload(self):
        db = FakeDB()
        payload = {
            "id": "session-1",
            "user_id": "user-1",
            "title": "My crop issue",
            "category": "General",
            "messages": [],
        }

        await _save_session_to_store(db, "session-1", payload)

        self.assertIn("session-1", db.chat_history.docs)
        self.assertEqual(db.chat_history.docs["session-1"]["user_id"], "user-1")
        self.assertEqual(db.chat_history.docs["session-1"]["title"], "My crop issue")


if __name__ == "__main__":
    unittest.main()
