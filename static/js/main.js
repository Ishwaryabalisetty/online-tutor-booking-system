// ===== AUTO DISMISS ALERTS =====
document.addEventListener('DOMContentLoaded', () => {
  const alerts = document.querySelectorAll('.alert')
  alerts.forEach(alert => {
    setTimeout(() => {
      alert.style.transition = 'opacity 0.5s ease'
      alert.style.opacity = '0'
      setTimeout(() => alert.remove(), 500)
    }, 3500)
  })

  // ===== ANIMATE ELEMENTS ON LOAD =====
  const cards = document.querySelectorAll('.card, .stat-card, .tutor-card')
  cards.forEach((card, i) => {
    card.style.animationDelay = `${i * 0.07}s`
    card.classList.add('fade-up')
  })

  // ===== SEARCH FILTER =====
  const searchInput = document.getElementById('search-input')
  const subjectFilter = document.getElementById('subject-filter')

  if (searchInput) {
    searchInput.addEventListener('input', filterTutors)
  }
  if (subjectFilter) {
    subjectFilter.addEventListener('change', () => {
      document.getElementById('filter-form').submit()
    })
  }

  // ===== CONFIRM CANCEL =====
  document.querySelectorAll('.cancel-btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
      if (!confirm('Are you sure you want to cancel this booking?')) {
        e.preventDefault()
      }
    })
  })

  // ===== MOBILE NAV TOGGLE =====
  const menuBtn = document.getElementById('menu-btn')
  const navLinks = document.getElementById('nav-links')
  if (menuBtn && navLinks) {
    menuBtn.addEventListener('click', () => {
      navLinks.classList.toggle('open')
    })
  }

  // ===== ANIMATE STAT NUMBERS =====
  document.querySelectorAll('.stat-value[data-count]').forEach(el => {
    const target = parseInt(el.getAttribute('data-count'))
    let current = 0
    const step = Math.ceil(target / 40)
    const timer = setInterval(() => {
      current = Math.min(current + step, target)
      el.textContent = current
      if (current >= target) clearInterval(timer)
    }, 30)
  })
})

// ===== LIVE SEARCH FILTER =====
function filterTutors() {
  const query = document.getElementById('search-input').value.toLowerCase()
  const cards = document.querySelectorAll('.tutor-card')
  let visible = 0
  cards.forEach(card => {
    const text = card.textContent.toLowerCase()
    const show = text.includes(query)
    card.style.display = show ? '' : 'none'
    if (show) visible++
  })
  const noResult = document.getElementById('no-results')
  if (noResult) noResult.style.display = visible === 0 ? 'block' : 'none'
}

// ===== PASSWORD TOGGLE =====
function togglePassword(inputId) {
  const input = document.getElementById(inputId)
  const btn = input.nextElementSibling
  if (input.type === 'password') {
    input.type = 'text'
    btn.textContent = '🙈'
  } else {
    input.type = 'password'
    btn.textContent = '👁️'
  }
}

// ===== PASSWORD STRENGTH =====
function checkPasswordStrength(password) {
  const bar = document.getElementById('strength-bar')
  const text = document.getElementById('strength-text')
  if (!bar) return

  let strength = 0
  if (password.length >= 8) strength++
  if (/[A-Z]/.test(password)) strength++
  if (/[0-9]/.test(password)) strength++
  if (/[^A-Za-z0-9]/.test(password)) strength++

  const colors = ['#ef4444', '#f97316', '#eab308', '#22c55e']
  const labels = ['Weak', 'Fair', 'Good', 'Strong']
  const widths = ['25%', '50%', '75%', '100%']

  bar.style.width = password.length > 0 ? widths[strength - 1] || '10%' : '0'
  bar.style.background = colors[strength - 1] || '#ef4444'
  if (text) text.textContent = password.length > 0 ? labels[strength - 1] || 'Very Weak' : ''
}
