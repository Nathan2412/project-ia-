from flask import Flask, jsonify
import threading, time, sys, os, signal
import main  # ← ton script existant

app = Flask(__name__)

# ---------- endpoints ----------
@app.route("/api/health")
def health():
    return jsonify(status="ok")

@app.route("/api/stop", methods=["POST"])
def stop():
    os.kill(os.getpid(), signal.SIGINT)
    return {"status": "shutting down"}, 200

# ---------- thread métier ----------
def background_job():
    while True:
        try:
            main.main()          # une itération de ton algo
        except Exception as e:
            print("[BG] erreur :", e, file=sys.stderr)
        time.sleep(5)            # cadence (ajuste)

if __name__ == "__main__":
    threading.Thread(target=background_job, daemon=True).start()
    app.run(host="0.0.0.0", port=5000)
