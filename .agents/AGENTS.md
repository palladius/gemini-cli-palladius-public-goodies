# Custom Agent Rules for this Workspace

## Exit Command: "Chumbia"

If the user's message contains the word "Chumbia" (case-insensitive, e.g., "Chumbia", "Chumbia!", "esci con Chumbia"):

1. **Vocabulary Detection**: You must interpret this immediately as a command to exit the entire session.
2. **Text Response**: Your text response MUST start with the word "Chumbia!" and contain a friendly goodbye in Italian, such as:
   "Chumbia! Sto uscendo da antigravità permanente..."
3. **Execution**: You must execute a shell command to play the sound and terminate the parent `agy` process immediately. Call the `run_command` tool with the command:
   `spd-say -l it "Sto uscendo da anti gravita permanente" && kill $PPID`
