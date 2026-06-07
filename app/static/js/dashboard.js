/* ===============================
   AUTH GUARD
================================= */

const token = localStorage.getItem("access_token");

if (!token) {
  window.location.href = "/auth/login-page";
}

/* ===============================
   ELEMENT REFERENCES (SAFE)
================================= */

const totalCallsEl = document.getElementById("totalCalls");
const calls24hEl = document.getElementById("calls24h");
const mostUsedEl = document.getElementById("mostUsed");
const activeKeysEl = document.getElementById("activeKeys");
const keysTableBody = document.getElementById("keysTableBody");
const logoutBtn = document.getElementById("logoutBtn");

const createKeyBtn = document.getElementById("createKeyBtn");
const modalOverlay = document.getElementById("modalOverlay");
const closeModalBtn = document.getElementById("closeModalBtn");
const createKeyForm = document.getElementById("createKeyForm");

const successModal = document.getElementById("successModal");
const successKeyText = document.getElementById("successKeyText");
const closeSuccessBtn = document.getElementById("closeSuccessBtn");
const doneBtn = document.getElementById("doneBtn");
const copySuccessBtn = document.getElementById("copySuccessBtn");

const revokeModal = document.getElementById("revokeModal");
const closeRevokeBtn = document.getElementById("closeRevokeBtn");
const cancelRevokeBtn = document.getElementById("cancelRevokeBtn");
const confirmRevokeBtn = document.getElementById("confirmRevokeBtn");

let revokeTargetId = null;


/* ===============================
   LOGOUT
================================= */

if (logoutBtn) {
  logoutBtn.addEventListener("click", () => {
    localStorage.removeItem("access_token");
    window.location.href = "/auth/login-page";
  });
}

/* ===============================
   ANALYTICS
================================= */

async function loadAnalytics() {
  try {
    const res = await fetch("/keys/analytics", {
      headers: { Authorization: `Bearer ${token}` },
    });

    if (res.status === 401) {
      localStorage.removeItem("access_token");
      window.location.href = "/auth/login-page";
      return;
    }

    if (!res.ok) throw new Error("Analytics error");

    const data = await res.json();

    if (totalCallsEl) totalCallsEl.textContent = data.total_calls || 0;
    if (calls24hEl) calls24hEl.textContent = data.calls_last_24h || 0;
    if (mostUsedEl)
      mostUsedEl.textContent =
        data.most_used_endpoint?.endpoint || "-";
  } catch (err) {
    console.error("Analytics load failed:", err);
  }
}

/* ===============================
   LOAD KEYS
================================= */

async function loadKeys() {
  try {
    const res = await fetch("/keys/", {
      headers: { Authorization: `Bearer ${token}` },
    });

    if (!res.ok) throw new Error("Keys error");

    const keys = await res.json();

    if (!keysTableBody) return;

    keysTableBody.innerHTML = "";
    let activeCount = 0;

    keys.forEach((key) => {
      const isExpired =
        key.expires_at &&
        new Date(key.expires_at) < new Date();

      const isActive = key.is_active && !isExpired;

      if (isActive) activeCount++;

      const created = key.created_at
        ? new Date(key.created_at).toLocaleDateString()
        : "-";

      const expires = key.expires_at
        ? new Date(key.expires_at).toLocaleDateString()
        : "-";

      const row = document.createElement("tr");

      row.innerHTML = `
        <td>${key.name}</td>
        <td>${created}</td>
        <td>${expires}</td>
        <td>
          <span class="${
            isExpired
              ? "status-revoked"
              : isActive
              ? "status-active"
              : "status-revoked"
          }">
            ${
              isExpired
                ? "Expired"
                : isActive
                ? "Active"
                : "Revoked"
            }
          </span>
        </td>
        <td>${key.rate_limit_per_minute}/min</td>
        <td>
          ${
            isActive
              ? `<button class="revoke-btn">Revoke</button>`
              : `<span style="opacity:0.5;">Inactive</span>`
          }
          <button class="delete-btn">Delete</button>
        </td>
      `;

      const revokeBtn = row.querySelector(".revoke-btn");
      const deleteBtn = row.querySelector(".delete-btn");

      if (revokeBtn) {
        revokeBtn.addEventListener("click", () =>
          revokeKey(key._id)
        );
      }

      if (deleteBtn) {
        deleteBtn.addEventListener("click", () =>
          deleteKey(key._id)
        );
      }

      keysTableBody.appendChild(row);
    });

    if (activeKeysEl) activeKeysEl.textContent = activeCount;
  } catch (err) {
    console.error("Keys load failed:", err);
  }
}

/* ===============================
   REVOKE / DELETE
================================= */

function revokeKey(id) {
  revokeTargetId = id;
  if (revokeModal) revokeModal.classList.remove("hidden");
}

async function confirmRevoke() {
  if (!revokeTargetId) return;

  await fetch(`/keys/${revokeTargetId}/revoke`, {
    method: "PATCH",
    headers: { Authorization: `Bearer ${token}` },
  });

  revokeTargetId = null;
  closeRevokeModal();
  loadKeys();
  loadAnalytics();
}

function closeRevokeModal() {
  if (revokeModal) revokeModal.classList.add("hidden");
  revokeTargetId = null;
}

if (confirmRevokeBtn)
  confirmRevokeBtn.addEventListener("click", confirmRevoke);

if (cancelRevokeBtn)
  cancelRevokeBtn.addEventListener("click", closeRevokeModal);

if (closeRevokeBtn)
  closeRevokeBtn.addEventListener("click", closeRevokeModal);

if (revokeModal) {
  revokeModal.addEventListener("click", (e) => {
    if (e.target === revokeModal) closeRevokeModal();
  });
}


async function deleteKey(id) {
  await fetch(`/keys/${id}`, {
    method: "DELETE",
    headers: { Authorization: `Bearer ${token}` },
  });

  loadKeys();
  loadAnalytics();
}

/* ===============================
   CREATE KEY MODAL CONTROL
================================= */

if (createKeyBtn && modalOverlay) {
  createKeyBtn.addEventListener("click", () => {
    modalOverlay.classList.remove("hidden");
  });
}

if (closeModalBtn) {
  closeModalBtn.addEventListener("click", closeCreateModal);
}

if (modalOverlay) {
  modalOverlay.addEventListener("click", (e) => {
    if (e.target === modalOverlay) {
      closeCreateModal();
    }
  });
}

function closeCreateModal() {
  if (modalOverlay) modalOverlay.classList.add("hidden");
  if (createKeyForm) createKeyForm.reset();
}

/* ===============================
   CREATE KEY SUBMIT
================================= */

if (createKeyForm) {
  createKeyForm.addEventListener("submit", async (e) => {
    e.preventDefault();

    const name = document.getElementById("keyName")?.value;
    const expires =
      document.getElementById("expiresDays")?.value || 30;
    const rate =
      document.getElementById("rateLimit")?.value || 60;

    try {
      const res = await fetch("/keys/", {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          name,
          expires_in_days: parseInt(expires),
          rate_limit: parseInt(rate),
        }),
      });

      const data = await res.json();

      if (!res.ok) throw new Error("Create failed");

      closeCreateModal();

      if (successKeyText)
        successKeyText.textContent = data.api_key;

      if (successModal)
        successModal.classList.remove("hidden");

      loadKeys();
      loadAnalytics();
    } catch (err) {
      console.error("Create key failed:", err);
    }
  });
}

/* ===============================
   SUCCESS MODAL CONTROL
================================= */

function closeSuccessModal() {
  if (successModal)
    successModal.classList.add("hidden");
}

if (closeSuccessBtn)
  closeSuccessBtn.addEventListener(
    "click",
    closeSuccessModal
  );

if (doneBtn)
  doneBtn.addEventListener(
    "click",
    closeSuccessModal
  );

if (successModal) {
  successModal.addEventListener("click", (e) => {
    if (e.target === successModal) {
      closeSuccessModal();
    }
  });
}

if (copySuccessBtn) {
  copySuccessBtn.addEventListener("click", () => {
    if (successKeyText)
      navigator.clipboard.writeText(
        successKeyText.textContent
      );
  });
}

/* ===============================
   INITIAL LOAD
================================= */

loadAnalytics();
loadKeys();
