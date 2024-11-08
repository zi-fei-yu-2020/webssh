<template>
  <div class="xtermbox">
    <div ref="xterm" class="xterm"></div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick } from "vue";
import "@xterm/xterm/css/xterm.css";
import { Terminal } from "@xterm/xterm";
import { FitAddon } from "@xterm/addon-fit";
import { AttachAddon } from "@xterm/addon-attach";

// Props
const props = defineProps({
  fontSize: {
    type: Number,
    default: 15,
  },
  wsuri: {
    type: String,
    default: "",
  },
});

// Refs
const xterm = ref(null);
const term = ref(null);
const ws = ref(null);
const fitAddon = ref(new FitAddon());
const attachAddon = ref(null);

// Initialize xterm
const initXterm = () => {
  term.value = new Terminal({
    rendererType: "canvas",
    fontSize: props.fontSize,
    scrollback: 500,
    convertEol: true,
    cursorBlink: true,
    disableStdin: false,
    cursorStyle: "block",
    theme: {
      foreground: "yellow",
      background: "black",
      cursor: "yellow",
    },
  });

  term.value.loadAddon(fitAddon.value);
  term.value.open(xterm.value);
  console.log("xterm initialized and opened");

  // Adjust terminal size after initialization
  nextTick(() => {
    fitAddon.value.fit();
    console.log("Terminal fitted to container");
  });
};

// Initialize WebSocket with delay
const initSocket = () => {
  ws.value = new WebSocket(props.wsuri);

  ws.value.onopen = () => {
    console.log("WebSocket connection opened");
    attachAddon.value = new AttachAddon(ws.value);
    term.value.loadAddon(attachAddon.value);

    fitAddon.value.fit(); // Ensure the terminal fits the container

    term.value.write("Welcome To Django-Vue WebSSH ☺\r\n");
    termResize({ cols: term.value.cols, rows: term.value.rows });
  };

  ws.value.onclose = () => {
    console.log("WebSocket connection closed");
    term.value.write("\r\n连接已被关闭...\r\n");
    if (attachAddon.value) {
      attachAddon.value.dispose(); // Dispose addon only if it exists
      attachAddon.value = null; // Clear addon after disposing
    }
  };

  ws.value.onerror = () => {
    console.log("WebSocket error");
    if (attachAddon.value) {
      attachAddon.value.dispose(); // Dispose addon only if it exists
      attachAddon.value = null; // Clear addon after disposing
    }
    ws.value.close();
    ws.value = null;
    setTimeout(reconnect, 3000); // Retry connection after 3 seconds
  };

  term.value.onData((data) => {
    if (!ws.value || ws.value.readyState >= WebSocket.CLOSING) {
      term.value.write("\r\n连接丢失,正在尝试重新连接!\r\n");
      reconnect();
    }
  });

  term.value.onResize(({ cols, rows }) => {
    fitAddon.value.fit();
    termResize({ cols, rows });
  });
};

// Resize Terminal
const termResize = (size) => {
  if (ws.value) {
    size["resize"] = 1;
    ws.value.send(JSON.stringify(size));
  }
};

// Handle window resize
const listenResize = () => {
  if (fitAddon.value) {
    fitAddon.value.fit();
    term.value.focus();
  }
};

// Reconnect WebSocket
const reconnect = () => {
  if (!ws.value || ws.value.readyState >= WebSocket.CLOSING) {
    initSocket();
  }
};

// Lifecycle hooks
onMounted(() => {
  console.log("Component mounted");
  initXterm();

  // Delay WebSocket initialization to ensure xterm is ready
  setTimeout(() => {
    console.log("Initializing WebSocket connection after delay");
    initSocket();
  }, 500); // Adjust delay as necessary

  window.addEventListener("resize", listenResize);
});

onUnmounted(() => {
  if (ws.value) ws.value.close();
  if (attachAddon.value) attachAddon.value.dispose(); // Dispose properly
  window.removeEventListener("resize", listenResize);
});
</script>

<style lang="scss" scoped>
.xtermbox {
  width: 100%;
  height: 100%;
  background: black;
  .xterm {
    width: 100%;
    height: calc(100vh - 64px);
    top: 64px;
    position: absolute;
  }
}
.xterm {
  position: absolute;
  left: 0;
  top: 0;
  width: 100%;
  height: 100%;
  overflow: auto;
}
</style>
