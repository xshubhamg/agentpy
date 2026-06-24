import os
import time
import threading
from typing import Annotated, Any

# Simple in-memory note storage for the session, or file based?
# User requested "modularity", let's use a file.
NOTES_FILE = "agent_notes.txt"

def register(agent: Any) -> None:
    @agent.tool
    def write_note(content: Annotated[str, "The note content to save"]) -> dict[str, str]:
        """Append a note to the local notes file."""
        try:
            with open(NOTES_FILE, "a") as f:
                f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {content}\n")
            return {"status": "success", "message": "Note saved."}
        except Exception as e:
            return {"error": str(e)}

    @agent.tool
    def read_notes() -> dict[str, Any]:
        """Read all notes from the local notes file."""
        try:
            if not os.path.exists(NOTES_FILE):
                return {"notes": []}
            with open(NOTES_FILE, "r") as f:
                return {"notes": f.readlines()}
        except Exception as e:
            return {"error": str(e)}

    @agent.tool
    def set_timer(
        seconds: Annotated[int, "Number of seconds to wait"],
        label: Annotated[str, "Label for the timer"] = "Timer"
    ) -> dict[str, str]:
        """Start a background timer that prints a message when finished."""
        def timer_thread():
            time.sleep(seconds)
            # In a real CLI, we might need a way to notify the user.
            # For now, we just log it or rely on the agent's turn being over.
            print(f"\n[TIMER] '{label}' finished after {seconds} seconds!")

        threading.Thread(target=timer_thread, daemon=True).start()
        return {"status": "success", "message": f"Timer '{label}' set for {seconds} seconds."}
