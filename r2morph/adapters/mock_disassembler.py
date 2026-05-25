"""Mock disassembler for testing purposes.

This module provides a mock implementation of DisassemblerInterface that
can be used in tests to avoid the need for actual radare2 installation
and binary analysis.
"""

from pathlib import Path
from typing import Any

from r2morph.protocols import DisassemblerInterface


class MockDisassembler:
    """Mock disassembler for testing purposes.

    This mock allows tests to define expected responses for specific commands,
    enabling deterministic testing without actual disassembler operations.

    Example usage in tests:
        mock = MockDisassembler()
        mock.set_response("ij", {"bin": {"arch": "x86", "bits": 64}})
        mock.set_response("aflj", [{"name": "main", "offset": 0x1000}])

        mock.open(Path("/fake/binary"))
        assert mock.cmdj("ij")["bin"]["arch"] == "x86"
        mock.close()

    You can also pre-populate responses during construction:
        mock = MockDisassembler(responses={
            "ij": {"bin": {"arch": "x86"}},
            "aflj": [{"name": "main"}]
        })
    """

    def __init__(self, responses: dict[str, Any] | None = None) -> None:
        """Initialize the mock with optional pre-configured responses.

        Args:
            responses: Dictionary mapping commands to their responses.
        """
        self._responses: dict[str, Any] = responses.copy() if responses else {}
        self._is_open: bool = False
        self._opened_path: Path | None = None
        self._opened_flags: list[str] | None = None
        self._command_history: list[str] = []

    def set_response(self, command: str, response: Any) -> None:
        """Set the response for a specific command.

        Args:
            command: The command string to match.
            response: The response to return when the command is executed.
        """
        pass

    def set_responses(self, responses: dict[str, Any]) -> None:
        """Set multiple responses at once.

        Args:
            responses: Dictionary mapping commands to their responses.
        """
        pass

    def clear_responses(self) -> None:
        """Clear all configured responses."""
        pass

    def open(self, path: Path, flags: list[str] | None = None) -> None:
        """Open a mock binary for analysis.

        Args:
            path: Path to the binary (not actually accessed).
            flags: Optional flags (stored for inspection in tests).
        """
        pass

    def close(self) -> None:
        """Close the mock connection."""
        self._is_open = False

    def cmd(self, command: str) -> str:
        """Execute a command and return the configured string response.

        Args:
            command: The command to execute.

        Returns:
            The configured string response, or empty string if not configured.

        Raises:
            RuntimeError: If the mock is not open.
        """
        if not self._is_open:
            raise RuntimeError("Disassembler not open")

        self._command_history.append(command)
        response = self._responses.get(command, "")
        return str(response)

    def cmdj(self, command: str) -> Any:
        """Execute a command and return the configured JSON response.

        Args:
            command: The command to execute.

        Returns:
            The configured response, or empty dict if not configured.

        Raises:
            RuntimeError: If the mock is not open.
        """
        if not self._is_open:
            raise RuntimeError("Disassembler not open")

        self._command_history.append(command)
        return self._responses.get(command, {})

    def is_open(self) -> bool:
        """Check if the mock connection is open.

        Returns:
            True if open() was called without a subsequent close().
        """
        pass

    # Test helper methods

    @property
    def opened_path(self) -> Path | None:
        """Get the path that was passed to open()."""
        pass

    @property
    def opened_flags(self) -> list[str] | None:
        """Get the flags that were passed to open()."""
        pass

    @property
    def command_history(self) -> list[str]:
        """Get the list of commands that were executed."""
        pass

    def assert_command_called(self, command: str) -> None:
        """Assert that a specific command was called.

        Args:
            command: The command to check for.

        Raises:
            AssertionError: If the command was not called.
        """
        pass

    def assert_command_not_called(self, command: str) -> None:
        """Assert that a specific command was not called.

        Args:
            command: The command to check for.

        Raises:
            AssertionError: If the command was called.
        """
        pass


# Type assertion to verify MockDisassembler implements DisassemblerInterface
def _verify_protocol() -> DisassemblerInterface:
    """Static verification that MockDisassembler implements DisassemblerInterface.

    Never called; mypy checks the return type to assert structural
    conformance of MockDisassembler to DisassemblerInterface.
    """
    pass
