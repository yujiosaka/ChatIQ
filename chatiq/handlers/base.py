import chatiq


class BaseHandler:
    """Base class for handling Slack events.

    Attributes:
        chatiq: An instance of the ChatIQ class.
    """

    def __init__(self, chatiq: "chatiq.ChatIQ") -> None:
        """Initializes the BaseHandler with a ChatIQ instance.

        Args:
            chatiq: An instance of the ChatIQ class.
        """

        self.chatiq = chatiq

    def __call__(self, *args, **kwargs) -> None:
        """Handles mentions of the bot in Slack.

        Args:
            body: The event data.
            client: The Slack client.
            logger: The logger to use to log any errors.
            say: The function to use to send a message.
            ack (Callable[..., None]): Acknowledgement function to respond to the event.
        """

        raise NotImplementedError("You must implement the __call__ method")
