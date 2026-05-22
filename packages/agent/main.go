package main

import (
	"crypto/sha256"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"os"
	"os/exec"
	"os/signal"
	"strings"
	"syscall"
	"time"

	"github.com/fatedier/frp/cmd/frpc/sub"
)

// AppConfig maps the structure of config.json
type AppConfig struct {
	ClientID       string `json:"client_id"`
	Token          string `json:"token"`
	ApiURL         string `json:"api_url"`
	FrpcPath       string `json:"frpc_path"`
	FrpcConfigFile string `json:"frpc_config_file"`
	CheckInterval  int    `json:"check_interval"`
}

// ProxyConfig maps the proxies in central API
type ProxyConfig struct {
	Name       string `json:"name"`
	Type       string `json:"type"`
	LocalIP    string `json:"localIP"`
	LocalPort  int    `json:"localPort"`
	RemotePort int    `json:"remotePort"`
	Enabled    bool   `json:"enabled"`
}

// RemoteConfig maps the central API response
type RemoteConfig struct {
	Common  map[string]interface{} `json:"common"`
	Proxies []ProxyConfig          `json:"proxies"`
}

func main() {
	// If first argument is "run-frpc", we run the embedded FRP client
	if len(os.Args) > 1 && os.Args[1] == "run-frpc" {
		os.Args = append([]string{os.Args[0]}, os.Args[2:]...)
		sub.Execute()
		return
	}

	// Run main agent manager
	runAgentManager()
}

func runAgentManager() {
	fmt.Println("[INFO] Starting Go KannnHole Client Agent...")

	// Load configuration
	cfg, err := loadConfig("config.json")
	if err != nil {
		fmt.Printf("[ERROR] Failed to load config.json: %v\n", err)
		os.Exit(1)
	}

	// Capture termination signals to stop child process cleanly
	sigChan := make(chan os.Signal, 1)
	signal.Notify(sigChan, syscall.SIGINT, syscall.SIGTERM)

	var frpcCmd *exec.Cmd
	lastHash := ""

	// Helper function to stop frpc
	stopFrpc := func() {
		if frpcCmd != nil && frpcCmd.Process != nil {
			fmt.Println("[INFO] Stopping frpc process...")
			// Send SIGTERM
			_ = frpcCmd.Process.Signal(syscall.SIGTERM)
			
			// Wait with timeout
			done := make(chan error, 1)
			go func() {
				done <- frpcCmd.Wait()
			}()

			select {
			case <-done:
				fmt.Println("[INFO] frpc stopped cleanly.")
			case <-time.After(5 * time.Second):
				fmt.Println("[WARN] frpc did not stop, killing...")
				_ = frpcCmd.Process.Kill()
				<-done
			}
			frpcCmd = nil
		}
	}

	// Handle cleanup on exit
	go func() {
		<-sigChan
		fmt.Println("\n[INFO] Termination signal received.")
		stopFrpc()
		os.Exit(0)
	}()

	checkInterval := cfg.CheckInterval
	if checkInterval <= 0 {
		checkInterval = 30
	}

	for {
		fmt.Println("[INFO] Checking remote configuration...")
		remoteJSON, err := fetchRemoteConfig(cfg.ApiURL, cfg.Token)
		if err != nil {
			fmt.Printf("[WARN] Failed to fetch remote config: %v\n", err)
		} else {
			currentHash := calculateHash(remoteJSON)
			if currentHash != lastHash {
				fmt.Println("[INFO] Configuration changed, reloading...")
				
				var remoteCfg RemoteConfig
				if err := json.Unmarshal(remoteJSON, &remoteCfg); err != nil {
					fmt.Printf("[ERROR] Failed to parse remote config: %v\n", err)
				} else {
					// Convert and write TOML config
					tomlContent := convertToTOML(remoteCfg)
					if err := os.WriteFile(cfg.FrpcConfigFile, []byte(tomlContent), 0644); err != nil {
						fmt.Printf("[ERROR] Failed to write TOML config: %v\n", err)
					} else {
						// Stop running process if active
						stopFrpc()

						// Start new process
						exePath, err := os.Executable()
						if err != nil {
							// fallback to os.Args[0]
							exePath = os.Args[0]
						}

						fmt.Println("[INFO] Starting frpc process...")
						frpcCmd = exec.Command(exePath, "run-frpc", "-c", cfg.FrpcConfigFile)
						frpcCmd.Stdout = os.Stdout
						frpcCmd.Stderr = os.Stderr

						if err := frpcCmd.Start(); err != nil {
							fmt.Printf("[ERROR] Failed to start frpc: %v\n", err)
						} else {
							lastHash = currentHash
							fmt.Println("[INFO] frpc started successfully.")
						}
					}
				}
			} else {
				fmt.Println("[INFO] Configuration has not changed.")
			}
		}

		time.Sleep(time.Duration(checkInterval) * time.Second)
	}
}

func loadConfig(path string) (*AppConfig, error) {
	data, err := os.ReadFile(path)
	if err != nil {
		return nil, err
	}
	var cfg AppConfig
	if err := json.Unmarshal(data, &cfg); err != nil {
		return nil, err
	}
	return &cfg, nil
}

func fetchRemoteConfig(url, token string) ([]byte, error) {
	req, err := http.NewRequest("GET", url, nil)
	if err != nil {
		return nil, err
	}
	req.Header.Set("X-Auth-Token", token)

	client := &http.Client{Timeout: 10 * time.Second}
	resp, err := client.Do(req)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("unexpected status code: %d", resp.StatusCode)
	}

	return io.ReadAll(resp.Body)
}

func calculateHash(data []byte) string {
	hasher := sha256.New()
	hasher.Write(data)
	return fmt.Sprintf("%x", hasher.Sum(nil))
}

func convertToTOML(cfg RemoteConfig) string {
	var sb strings.Builder

	// Write common configuration in TOML format compatible with modern frp v0.52.0+
	sb.WriteString("# Generated by KannnHole Agent\n\n")
	
	serverAddr, _ := cfg.Common["server_addr"].(string)
	if serverAddr == "" {
		serverAddr = "127.0.0.1"
	}
	sb.WriteString(fmt.Sprintf("serverAddr = %q\n", serverAddr))

	serverPortVal := cfg.Common["server_port"]
	var serverPort int
	switch v := serverPortVal.(type) {
	case float64:
		serverPort = int(v)
	case int:
		serverPort = v
	default:
		serverPort = 7000
	}
	sb.WriteString(fmt.Sprintf("serverPort = %d\n", serverPort))

	token, _ := cfg.Common["token"].(string)
	sb.WriteString("auth.method = \"token\"\n")
	sb.WriteString(fmt.Sprintf("auth.token = %q\n\n", token))

	// Write proxy configurations
	for _, p := range cfg.Proxies {
		if !p.Enabled {
			continue
		}
		sb.WriteString("[[proxies]]\n")
		sb.WriteString(fmt.Sprintf("name = %q\n", p.Name))
		
		pType := p.Type
		if pType == "" {
			pType = "tcp"
		}
		sb.WriteString(fmt.Sprintf("type = %q\n", pType))

		localIP := p.LocalIP
		if localIP == "" {
			localIP = "127.0.0.1"
		}
		sb.WriteString(fmt.Sprintf("localIP = %q\n", localIP))
		sb.WriteString(fmt.Sprintf("localPort = %d\n", p.LocalPort))
		sb.WriteString(fmt.Sprintf("remotePort = %d\n\n", p.RemotePort))
	}

	return sb.String()
}
