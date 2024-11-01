# this must be sourced

PROMPT_SCRIPT="/usr/local/bin/"

function AskForTip() {
    local exit_code=$?
    python3 "$PROMPT_SCRIPT"
}

[ ${ZSH_VERSION} ] && precmd() { AskForTip; }

[ ${BASH_VERSION} ] && PROMPT_COMMAND='AskForTip'
 
