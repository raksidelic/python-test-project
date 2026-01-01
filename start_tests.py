import platform
import os
import subprocess
import sys
import tempfile
from pathlib import Path

# --- DOTENV ---
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("⚠️  WARNING: 'python-dotenv' library not installed. .env file might not be read.")
    print("👉 To install: pip install python-dotenv")
# -------------------------------------

# --- DOCKERFILE TEMPLATE ---
DOCKERFILE_TEMPLATE = """
FROM alpine:latest
RUN apk add --no-cache ffmpeg bash xset pulseaudio-utils
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
"""

def is_docker_running():
    """Checks if Docker Daemon is running."""
    try:
        subprocess.run(["docker", "info"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def check_image_exists(image_name):
    """Checks if the specified image exists in Docker."""
    try:
        result = subprocess.run(
            ["docker", "images", "-q", image_name],
            capture_output=True,
            text=True
        )
        return bool(result.stdout.strip())
    except subprocess.CalledProcessError:
        return False

def build_arm_native_recorder(target_image_name):
    original_image = "selenoid/video-recorder:latest-release"
    
    print(f"   🛠️  ATTENTION: '{target_image_name}' not found. Automatic build process starting...")
    
    # 1. Original Image Check (Offline Support)
    if check_image_exists(original_image):
        print(f"   ✅ Original source image ({original_image}) found locally. Will not be pulled from internet.")
    else:
        print(f"   📥 Original image not found locally, pulling from internet: {original_image}")
        try:
            subprocess.run(["docker", "pull", original_image], check=True, stdout=subprocess.DEVNULL) # Keep stderr open
        except subprocess.CalledProcessError:
            print(f"   ❌ ERROR: Could not pull '{original_image}'. Check your internet connection or Docker.")
            sys.exit(1)
    
    # Temporary directory operation
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        script_path = temp_path / "entrypoint.sh"
        dockerfile_path = temp_path / "Dockerfile"
        
        # 2. Extract entrypoint.sh from original image
        print("   📄 Copying entrypoint.sh from original image...")
        try:
            with open(script_path, "w") as f:
                # stderr=DEVNULL added to hide platform warning (amd64/arm64 mismatch)
                subprocess.run(
                    ["docker", "run", "--rm", "--entrypoint", "cat", original_image, "/entrypoint.sh"],
                    stdout=f,
                    stderr=subprocess.DEVNULL, 
                    check=True
                )
        except subprocess.CalledProcessError:
             print("   ❌ ERROR: Could not copy entrypoint.sh!")
             sys.exit(1)
        
        if script_path.stat().st_size == 0:
            print("   ❌ ERROR: Extracted entrypoint.sh is empty!")
            sys.exit(1)
            
        # 3. Create Dockerfile
        print("   📝 Creating Dockerfile...")
        with open(dockerfile_path, "w") as f:
            f.write(DOCKERFILE_TEMPLATE.strip())
            
        # 4. Build New Image
        print(f"   🔨 Building Native ARM image: {target_image_name}")
        try:
            subprocess.run(
                ["docker", "build", "-t", target_image_name, "."],
                cwd=temp_dir,
                check=True
            )
            print("   ✅ Image successfully built!")
        except subprocess.CalledProcessError:
            print("   ❌ ERROR: Issue occurred while building image.")
            sys.exit(1)
            
    print("   🧹 Temporary files cleaned.")

def main():
    # 0. Docker Health Check
    if not is_docker_running():
        print("❌ CRITICAL ERROR: Docker is not running! Please start Docker Desktop.")
        sys.exit(1)

    arch = platform.machine().lower()
    system = platform.system()
    
    print(f"🖥️  Scanning System... OS: {system} | Processor: {arch}")

    browsers_json = None
    video_image = None
    
    # --- 1. ARCHITECTURE CHECK ---
    if any(x in arch for x in ["arm", "aarch64"]):
        print("✅ Detection: ARM Architecture (Apple Silicon)")
        browsers_json = "browsers_arm.json"
        video_image = "selenoid/video-recorder:arm-native"
        auto_worker_count = "3"
        
        if not check_image_exists(video_image):
            build_arm_native_recorder(video_image)
        
        print("   📦 Checking ARM Browser Images...")

        arm_images = [
            "seleniarm/standalone-chromium:latest",
            "seleniarm/standalone-firefox:latest"
        ]

        for img in arm_images:
            if check_image_exists(img):
                print(f"     ✅ Ready: {img}")
            else:
                print(f"     📥 Downloading: {img}")
                subprocess.run(["docker", "pull", img], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    elif any(x in arch for x in ["x86_64", "amd64", "i386", "i686"]):
        print("✅ Detection: Intel/AMD Architecture")
        browsers_json = "browsers_intel.json"
        video_image = "selenoid/video-recorder:latest-release"
        auto_worker_count = "2"
        
        print("   📦 Checking Intel Browser Images...")

        intel_images = [
            "selenoid/vnc:chrome_120.0",
            "selenoid/vnc:firefox_120.0",
            video_image # Added official recorder to list for Intel
        ]

        for img in intel_images:
            if check_image_exists(img):
                print(f"     ✅ Ready: {img}")
            else:
                print(f"     📥 Downloading: {img}")
                subprocess.run(["docker", "pull", img], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    else:
        print(f"❌ ERROR: Architecture not recognized ({arch}).")
        sys.exit(1)

    # --- 2. EXECUTION ---
    final_worker_count = os.getenv("WORKER_COUNT", auto_worker_count)
    
    # --- CLEANUP POLICY ---
    is_ci = os.getenv("CI", "false").lower() == "true"
    default_policy = "never" if is_ci else "on_failure"
    keep_containers_policy = os.getenv("KEEP_CONTAINERS", default_policy).lower()
    # -------------------------------------------------

    if browsers_json and video_image:
        print("\n🚀 Starting Test Environment...")
        print(f"   ⚙️ Cleanup Policy (KEEP_CONTAINERS): {keep_containers_policy}")
        print(f"   📄 Browser Config : {browsers_json}")
        print(f"   🎥 Video Image    : {video_image}")
        
        if final_worker_count != auto_worker_count:
            print(f"   ⚠️ MANUAL SETTING: Worker count set to {final_worker_count}.")
        else:
            print(f"   ⚡ Auto Worker: {final_worker_count}")
        
        env = os.environ.copy()
        env["BROWSERS_JSON"] = browsers_json
        env["VIDEO_RECORDER_IMAGE"] = video_image
        env["WORKER_COUNT"] = final_worker_count
        
        exit_code = 1 # Default error code
        user_aborted = False # Track user interruption

        try:
            print("🧹 Cleaning up...")
            # 1. Infrastructure Cleanup (Compose)
            subprocess.run(["docker-compose", "down", "--remove-orphans"], env=env, stderr=subprocess.DEVNULL)
            
            # 2. Worker Cleanup (Aggressive)
            # Deletes browser/video leftovers from old sessions.
            force_clean_cmd = "docker ps -a --format '{{.ID}} {{.Image}}' | grep -E 'selenoid|seleniarm' | grep -v 'aerokube' | awk '{print $1}' | xargs docker rm -f 2>/dev/null"
            subprocess.run(force_clean_cmd, shell=True)
            
            print("🎬 Starting Containers...")
            result = subprocess.run(
                ["docker-compose", "up", "--build", "--exit-code-from", "pytest-tests"], 
                env=env
            )
            exit_code = result.returncode

            if exit_code == 130:
                print("\n🛑 Stopped by user (Exit 130).")
                exit_code = 0
                user_aborted = True

        except KeyboardInterrupt:
            print("\n🛑 Stopped by user.")
            exit_code = 0
            user_aborted = True
        except Exception as e:
            print(f"❌ Error: {e}")
            exit_code = 1
        finally:
            # --- CLEANUP LOGIC ---
            should_cleanup = True # Default

            if keep_containers_policy in ["true", "always"]:
                should_cleanup = False
                print(f"\n🛡️  KEEP_CONTAINERS={keep_containers_policy}: System left running.")
            
            elif keep_containers_policy == "on_failure":
                if exit_code != 0 and not user_aborted: # If failed AND not aborted by user
                    should_cleanup = False
                    print(f"\n⚠️  Test Failed (Exit: {exit_code}) and Policy=on_failure.")
                    print("🐛 System left RUNNING for debugging.")
                else:
                    print("\n✅ Tests Successful: Cleaning up system.")

            elif keep_containers_policy in ["false", "never"]:
                should_cleanup = True
                print(f"\n🧹 KEEP_CONTAINERS={keep_containers_policy}: Forced cleanup.")

            # Show Debug Info
            if not should_cleanup:
                print("👉 UI Address: http://localhost:8080")
                print("🧹 To clean: 'docker-compose down'")
            
            # Action 1: Infrastructure Cleanup
            if should_cleanup:
                print("\n🧹 System cleaning (Teardown)...")
                subprocess.run(["docker-compose", "down", "--remove-orphans"], env=env, stderr=subprocess.DEVNULL)
            
            # Action 2: Worker Cleanup (ALWAYS)
            # Regardless of policy, browsers and recorders must be deleted when finished or aborted.
            # Selenoid Hub and UI are preserved thanks to 'aerokube' filter.
            print("🚿 Cleaning workers...")
            try:
                force_clean_cmd = "docker ps -a --format '{{.ID}} {{.Image}}' | grep -E 'selenoid|seleniarm' | grep -v 'aerokube' | awk '{print $1}' | xargs docker rm -f 2>/dev/null"
                subprocess.run(force_clean_cmd, shell=True)
                print("✨ Cleanup complete.")
            except Exception:
                pass

            sys.exit(exit_code)

if __name__ == "__main__":
    main()