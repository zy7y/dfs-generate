import pytest
from dfs_generate.client import get_unused_port, desktop_client


# 由于get_unused_port函数依赖于随机性和系统状态，我们倾向于对socket操作进行mock
@pytest.mark.parametrize("mocked_port", [12345])
def test_get_unused_port(mocker, mocked_port):
    # Mocking the socket operations
    mock_socket = mocker.patch("dfs_generate.client.socket.socket")
    mock_socket.bind.return_value = None
    mock_socket.close.return_value = None

    # To ensure we control the behavior of randint for predictable testing
    mock_randint = mocker.patch("dfs_generate.client.random.randint")
    mock_randint.return_value = mocked_port

    # Test the function
    port = get_unused_port()
    assert port == mocked_port
    mock_socket.bind.assert_called_once_with(("localhost", mocked_port))
    mock_socket.close.assert_called_once()


@pytest.fixture
def mock_app_run(mocker):
    """Fixture to mock app.run method."""
    mock_run = mocker.patch("dfs_generate.server.app.run")
    yield mock_run


@pytest.fixture
def mock_webview(mocker):
    """Fixture to mock webview functions."""
    mock_create_window = mocker.patch("webview.create_window")
    mock_start = mocker.patch("webview.start")
    yield mock_create_window, mock_start


def test_desktop_client(mock_app_run, mock_webview):
    """Test the desktop_client function."""
    # Since get_unused_port is mocked in test_get_unused_port, we can assume it works.
    # Here we focus on verifying app.run and webview interactions.
    desktop_client()

    mock_app_run.assert_called_once_with(
        port=12345
    )  # Assuming 12345 is a typical port used in tests
    create_window, start = mock_webview
    create_window.assert_called_once_with("DFS代码生成", "http://127.0.0.1:12345")
    start.assert_called_once()
