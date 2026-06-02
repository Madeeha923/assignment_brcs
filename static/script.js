// API Base URL
const API_BASE = '/api';

// Form Submission
async function submitAppointment(e) {
    e.preventDefault();

    const form = e.target;
    const submitBtn = form.querySelector('button[type="submit"]');
    const successMsg = document.getElementById('successMessage');
    const errorMsg = document.getElementById('errorMessage');

    // Clear previous messages
    successMsg.style.display = 'none';
    errorMsg.style.display = 'none';

    // Clear errors
    clearFormErrors();

    // Validate form
    if (!validateForm()) {
        return;
    }

    // Disable submit button
    submitBtn.disabled = true;
    submitBtn.innerHTML = 'Booking...';

    try {
        const formData = new FormData(form);

        const response = await fetch(`${API_BASE}/appointments`, {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (response.ok) {
            // Show success message
            document.getElementById('successText').innerHTML = `
                <p>Your appointment has been booked successfully!</p>
                <p>Appointment Time: ${formatDateTime(data.appointment.appointment_time)}</p>
                <p>${data.message}</p>
            `;
            successMsg.style.display = 'flex';

            // Reset form
            form.reset();

            // Redirect to dashboard after 3 seconds
            setTimeout(() => {
                window.location.href = '/dashboard';
            }, 3000);
        } else {
            // Show error message
            const errorText = data.detail || 'Failed to book appointment';
            document.getElementById('errorText').textContent = errorText;
            errorMsg.style.display = 'flex';
        }
    } catch (error) {
        console.error('Error:', error);
        document.getElementById('errorText').textContent = error.message || 'An error occurred';
        errorMsg.style.display = 'flex';
    } finally {
        submitBtn.disabled = false;
        submitBtn.innerHTML = 'Book Appointment';
    }
}

// Form Validation
function validateForm() {
    let isValid = true;

    // Validate name
    const name = document.getElementById('customerName').value.trim();
    if (name.length < 2) {
        document.getElementById('nameError').textContent = 'Name must be at least 2 characters';
        isValid = false;
    }

    // Validate phone
    const phone = document.getElementById('phoneNumber').value.trim();
    if (!isValidPhoneNumber(phone)) {
        document.getElementById('phoneError').textContent = 'Please enter a valid phone number';
        isValid = false;
    }

    // Validate appointment time
    const time = document.getElementById('appointmentTime').value;
    if (!time) {
        document.getElementById('timeError').textContent = 'Please select an appointment time';
        isValid = false;
    } else {
        const selectedTime = new Date(time);
        const now = new Date();
        if (selectedTime <= now) {
            document.getElementById('timeError').textContent = 'Appointment time must be in the future';
            isValid = false;
        }
    }

    return isValid;
}

// Clear form errors
function clearFormErrors() {
    document.getElementById('nameError').textContent = '';
    document.getElementById('phoneError').textContent = '';
    document.getElementById('timeError').textContent = '';
}

// Validate phone number
function isValidPhoneNumber(phone) {
    const cleaned = phone.replace(/\D/g, '');
    return cleaned.length >= 10;
}

// Dashboard Functions
let allAppointments = [];
let currentModal = null;

async function loadAppointments() {
    const loading = document.getElementById('loadingMessage');
    const empty = document.getElementById('emptyMessage');
    const list = document.getElementById('appointmentsList');

    loading.style.display = 'flex';
    list.innerHTML = '';

    try {
        const response = await fetch(`${API_BASE}/appointments`);
        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || 'Failed to load appointments');
        }

        allAppointments = data;
        loading.style.display = 'none';

        if (allAppointments.length === 0) {
            empty.style.display = 'flex';
        } else {
            empty.style.display = 'none';
            renderAppointments(allAppointments);
            updateStats(allAppointments);
        }
    } catch (error) {
        console.error('Error loading appointments:', error);
        loading.innerHTML = `<div class="alert-icon">✕</div><div>Error loading appointments: ${error.message}</div>`;
    }
}

function renderAppointments(appointments) {
    const list = document.getElementById('appointmentsList');
    list.innerHTML = '';

    if (appointments.length === 0) {
        return;
    }

    appointments.forEach(apt => {
        const card = createAppointmentCard(apt);
        list.appendChild(card);
    });
}

function createAppointmentCard(apt) {
    const card = document.createElement('div');
    card.className = 'appointment-card';
    card.onclick = () => showAppointmentModal(apt);

    const appointmentTime = new Date(apt.appointment_time);
    const now = new Date();
    const diffMinutes = Math.floor((appointmentTime - now) / (1000 * 60));

    let reminderStatus = '';
    if (diffMinutes > 0 && diffMinutes <= 60) {
        reminderStatus = '⏰ Within 1 hour';
    } else if (diffMinutes <= 0) {
        reminderStatus = '✓ Passed';
    }

    const statusClass = `status-${apt.status}`;

    card.innerHTML = `
        <div class="appointment-header">
            <div>
                <div class="appointment-name">${escapeHtml(apt.customer_name)}</div>
                <div class="appointment-status ${statusClass}">${apt.status}</div>
            </div>
        </div>
        <div class="appointment-details">
            <div class="detail-row">
                <span class="detail-label">📞 Phone:</span>
                <span class="detail-value">${apt.phone_number}</span>
            </div>
            <div class="detail-row">
                <span class="detail-label">📅 Appointment:</span>
                <span class="detail-value">${formatDateTime(apt.appointment_time)}</span>
            </div>
            <div class="detail-row">
                <span class="detail-label">📬 Status:</span>
                <span class="detail-value">
                    ${apt.confirmation_sent ? '✓ Confirmed' : '⏳ Confirming'} 
                    ${apt.reminder_sent ? '| ✓ Reminded' : ''}
                    ${reminderStatus ? `| ${reminderStatus}` : ''}
                </span>
            </div>
        </div>
        <div class="appointment-actions">
            <button class="btn btn-secondary btn-small" onclick="editAppointment(event, ${apt.id})">Edit</button>
            <button class="btn btn-primary btn-small" onclick="sendReminder(event, ${apt.id})">Send Reminder</button>
        </div>
    `;

    return card;
}

function showAppointmentModal(apt) {
    currentModal = apt;
    const modal = document.getElementById('appointmentModal');
    const body = document.getElementById('modalBody');

    body.innerHTML = `
        <div class="detail-row">
            <span class="detail-label">Name:</span>
            <span class="detail-value">${escapeHtml(apt.customer_name)}</span>
        </div>
        <div class="detail-row">
            <span class="detail-label">Phone:</span>
            <span class="detail-value">${apt.phone_number}</span>
        </div>
        <div class="detail-row">
            <span class="detail-label">Appointment Time:</span>
            <span class="detail-value">${formatDateTime(apt.appointment_time)}</span>
        </div>
        <div class="detail-row">
            <span class="detail-label">Created:</span>
            <span class="detail-value">${formatDateTime(apt.created_at)}</span>
        </div>
        <div class="detail-row">
            <span class="detail-label">Status:</span>
            <span class="detail-value">${apt.status}</span>
        </div>
        <div class="detail-row">
            <span class="detail-label">Confirmation Sent:</span>
            <span class="detail-value">${apt.confirmation_sent ? '✓ Yes' : '✗ No'}</span>
        </div>
        <div class="detail-row">
            <span class="detail-label">Reminder Sent:</span>
            <span class="detail-value">${apt.reminder_sent ? '✓ Yes' : '✗ No'}</span>
        </div>
    `;

    modal.style.display = 'flex';
}

function closeModal() {
    document.getElementById('appointmentModal').style.display = 'none';
    currentModal = null;
}

async function sendReminderManually() {
    if (!currentModal) return;

    const btn = document.getElementById('sendReminderBtn');
    btn.disabled = true;
    btn.innerHTML = 'Sending...';

    try {
        const response = await fetch(
            `${API_BASE}/reminders/${currentModal.id}/send-now`,
            { method: 'POST' }
        );
        const data = await response.json();

        if (response.ok) {
            alert('Reminder sent successfully!');
            closeModal();
            loadAppointments();
        } else {
            alert('Error sending reminder: ' + (data.detail || 'Unknown error'));
        }
    } catch (error) {
        alert('Error: ' + error.message);
    } finally {
        btn.disabled = false;
        btn.innerHTML = 'Send Reminder Now';
    }
}

async function deleteAppointment() {
    if (!currentModal) return;

    if (!confirm('Are you sure you want to delete this appointment?')) {
        return;
    }

    try {
        const response = await fetch(`${API_BASE}/appointments/${currentModal.id}`, {
            method: 'DELETE'
        });

        if (response.ok) {
            alert('Appointment deleted successfully');
            closeModal();
            loadAppointments();
        } else {
            const data = await response.json();
            alert('Error deleting appointment: ' + (data.detail || 'Unknown error'));
        }
    } catch (error) {
        alert('Error: ' + error.message);
    }
}

function sendReminder(event, appointmentId) {
    event.stopPropagation();

    const appointment = allAppointments.find(a => a.id === appointmentId);
    if (appointment) {
        currentModal = appointment;
        sendReminderManually();
    }
}

function editAppointment(event, appointmentId) {
    event.stopPropagation();
    // For now, just show the modal
    const appointment = allAppointments.find(a => a.id === appointmentId);
    if (appointment) {
        showAppointmentModal(appointment);
    }
}

function filterAppointments() {
    const search = document.getElementById('searchInput').value.toLowerCase();
    const status = document.getElementById('statusFilter').value;

    const filtered = allAppointments.filter(apt => {
        const matchSearch = 
            apt.customer_name.toLowerCase().includes(search) ||
            apt.phone_number.includes(search);
        const matchStatus = !status || apt.status === status;
        return matchSearch && matchStatus;
    });

    renderAppointments(filtered);
}

function updateStats(appointments) {
    const now = new Date();
    let upcoming = 0;
    let remindersSent = 0;

    appointments.forEach(apt => {
        const aptTime = new Date(apt.appointment_time);
        if (aptTime > now) {
            upcoming++;
        }
        if (apt.reminder_sent) {
            remindersSent++;
        }
    });

    document.getElementById('totalAppointments').textContent = appointments.length;
    document.getElementById('upcomingAppointments').textContent = upcoming;
    document.getElementById('remindersSent').textContent = remindersSent;
}

// Utility Functions
function formatDateTime(isoString) {
    const date = new Date(isoString);
    return date.toLocaleString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Close modal when clicking outside
window.addEventListener('click', (e) => {
    const modal = document.getElementById('appointmentModal');
    if (e.target === modal) {
        closeModal();
    }
});

// Set min date/time to now
document.addEventListener('DOMContentLoaded', () => {
    const timeInput = document.getElementById('appointmentTime');
    if (timeInput) {
        const now = new Date();
        now.setMinutes(now.getMinutes() - now.getTimezoneOffset());
        timeInput.min = now.toISOString().slice(0, 16);
    }
});
