from chatiq.document_loaders import DummyMessageLoader


def test_message_loader_load():
    loader = DummyMessageLoader()
    documents = loader.load()

    assert len(documents) == 1
