"use client";

import { useState, useEffect } from "react";
import {
  registerDevice,
  getDeviceStatus,
  revokeDevice,
  type DeviceRegistration,
  type DeviceStatus,
} from "@/lib/api";

interface DevicePairingProps {
  apiBase: string;
}

export function DevicePairing({ apiBase }: DevicePairingProps) {
  const [deviceId, setDeviceId] = useState<string | null>(null);
  const [deviceStatus, setDeviceStatus] = useState<DeviceStatus | null>(null);
  const [isRegistering, setIsRegistering] = useState(false);
  const [isChecking, setIsChecking] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  // Load device ID from localStorage on mount
  useEffect(() => {
    const storedDeviceId = localStorage.getItem("jarvis_device_id");
    if (storedDeviceId) {
      setDeviceId(storedDeviceId);
      checkDeviceStatus(storedDeviceId);
    }
  }, []);

  const handleRegister = async () => {
    setIsRegistering(true);
    setError(null);
    setSuccess(null);

    try {
      const result = await registerDevice(apiBase);
      setDeviceId(result.device_id);
      localStorage.setItem("jarvis_device_id", result.device_id);
      setSuccess(`Device registered successfully! Device ID: ${result.device_id}`);
      setDeviceStatus({
        device_id: result.device_id,
        status: result.certificate.status,
        revoked: false,
        created_at: result.certificate.created_at,
      });
    } catch (err: any) {
      setError(err.message || "Failed to register device");
    } finally {
      setIsRegistering(false);
    }
  };

  const checkDeviceStatus = async (id: string) => {
    setIsChecking(true);
    setError(null);

    try {
      const status = await getDeviceStatus(apiBase, id);
      setDeviceStatus(status);

      if (status.revoked) {
        setError("Device has been revoked. Please register a new device.");
        localStorage.removeItem("jarvis_device_id");
        setDeviceId(null);
      } else {
        setSuccess(`Device status: ${status.status}`);
      }
    } catch (err: any) {
      setError(err.message || "Failed to check device status");
    } finally {
      setIsChecking(false);
    }
  };

  const handleRevoke = async () => {
    if (!deviceId) return;

    if (!confirm("Are you sure you want to revoke this device? This action cannot be undone.")) {
      return;
    }

    setError(null);
    setSuccess(null);

    try {
      await revokeDevice(apiBase, deviceId);
      setSuccess("Device revoked successfully");
      localStorage.removeItem("jarvis_device_id");
      setDeviceId(null);
      setDeviceStatus(null);
    } catch (err: any) {
      setError(err.message || "Failed to revoke device");
    }
  };

  return (
    <div className="bg-slate-800/50 backdrop-blur-sm rounded-lg p-6 border border-slate-700/50">
      <h2 className="text-xl font-semibold text-white mb-4">Device Pairing</h2>

      {error && (
        <div className="mb-4 p-3 bg-red-500/20 border border-red-500/50 rounded text-red-200 text-sm">
          {error}
        </div>
      )}

      {success && (
        <div className="mb-4 p-3 bg-green-500/20 border border-green-500/50 rounded text-green-200 text-sm">
          {success}
        </div>
      )}

      {deviceId ? (
        <div className="space-y-4">
          <div className="p-4 bg-slate-700/30 rounded border border-slate-600/50">
            <div className="text-sm text-slate-300 mb-2">Device ID</div>
            <div className="font-mono text-xs text-slate-200 break-all">{deviceId}</div>
          </div>

          {deviceStatus && (
            <div className="p-4 bg-slate-700/30 rounded border border-slate-600/50">
              <div className="text-sm text-slate-300 mb-2">Status</div>
              <div className="flex items-center gap-2">
                <div
                  className={`w-2 h-2 rounded-full ${
                    deviceStatus.revoked
                      ? "bg-red-500"
                      : deviceStatus.status === "active"
                      ? "bg-green-500"
                      : "bg-yellow-500"
                  }`}
                />
                <span className="text-slate-200 capitalize">{deviceStatus.status}</span>
              </div>
              {deviceStatus.created_at && (
                <div className="text-xs text-slate-400 mt-2">
                  Created: {new Date(deviceStatus.created_at).toLocaleString()}
                </div>
              )}
            </div>
          )}

          <div className="flex gap-2">
            <button
              onClick={() => checkDeviceStatus(deviceId)}
              disabled={isChecking}
              className="px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-blue-800 disabled:opacity-50 text-white rounded text-sm transition-colors"
            >
              {isChecking ? "Checking..." : "Check Status"}
            </button>
            <button
              onClick={handleRevoke}
              className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded text-sm transition-colors"
            >
              Revoke Device
            </button>
          </div>
        </div>
      ) : (
        <div className="space-y-4">
          <p className="text-slate-300 text-sm">
            Register this device to enable Windows Companion features. The device will be paired
            using Ed25519 key exchange for secure communication.
          </p>
          <button
            onClick={handleRegister}
            disabled={isRegistering}
            className="px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-blue-800 disabled:opacity-50 text-white rounded text-sm transition-colors"
          >
            {isRegistering ? "Registering..." : "Register Device"}
          </button>
        </div>
      )}

      <div className="mt-4 pt-4 border-t border-slate-700/50">
        <div className="text-xs text-slate-400">
          <p className="mb-1">
            <strong>Security:</strong> Device keys are stored using Windows DPAPI (hardware-backed
            if TPM available).
          </p>
          <p>
            Device status is checked on each session. If revoked, all local credentials are
            cleared automatically.
          </p>
        </div>
      </div>
    </div>
  );
}

