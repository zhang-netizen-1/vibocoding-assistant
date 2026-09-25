const statusMessage = document.getElementById('flow-copy-status');

document.querySelectorAll('.flow-copy').forEach((button) => {
  button.addEventListener('click', async () => {
    const prompt = button.closest('.flow-card').querySelector('.flow-prompt-text').textContent.trim();
    try {
      await navigator.clipboard.writeText(prompt);
      statusMessage.textContent = `已复制「${button.closest('.flow-card').querySelector('h2').textContent}」实现提示词。`;
      const original = button.innerHTML;
      button.textContent = '已复制 ✓';
      window.setTimeout(() => { button.innerHTML = original; }, 1800);
    } catch {
      statusMessage.textContent = '复制失败，请手动选择提示词。';
    }
  });
});

const sampleForm = document.getElementById('sample-register');
sampleForm.addEventListener('submit', (event) => {
  event.preventDefault();
  const email = sampleForm.elements.email;
  const password = sampleForm.elements.password;
  const emailError = sampleForm.querySelector('[data-error="email"]');
  const passwordError = sampleForm.querySelector('[data-error="password"]');
  const status = sampleForm.querySelector('.flow-form-status');
  emailError.textContent = !email.value.trim() ? '请输入邮箱' : !email.validity.valid ? '请输入有效邮箱' : '';
  passwordError.textContent = !password.value ? '请输入密码' : password.value.length < 8 ? '密码至少 8 位' : '';
  email.setAttribute('aria-invalid', Boolean(emailError.textContent));
  password.setAttribute('aria-invalid', Boolean(passwordError.textContent));
  status.textContent = '';
  if (emailError.textContent || passwordError.textContent) {
    (emailError.textContent ? email : password).focus();
    return;
  }
  const button = sampleForm.querySelector('button[type="submit"]');
  button.disabled = true;
  button.textContent = '模拟提交中…';
  window.setTimeout(() => {
    button.disabled = false;
    button.innerHTML = '模拟提交 <span aria-hidden="true">↗</span>';
    status.textContent = '模拟提交完成，未创建真实账号。';
  }, 500);
});
