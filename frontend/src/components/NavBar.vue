<!-- 導覽列 (顯示 Logo、登入/登出按鈕) -->
 <!-- // 在你的 NavBar.vue 或任何登入按鈕的 click 事件
const handleLogin = () => {
  // 這裡需要填入你們 Cognito 的 Hosted UI 網址
  // 請跟負責 AWS 的組員拿 (Output 裡的 LoginURL 或自己拼湊)
  const cognitoDomain = 'https://<你的-domain>.auth.us-east-1.amazoncognito.com';
  const clientId = '<你的-App-Client-ID>';
  const redirectUri = 'http://localhost:5173/auth/callback'; // 本機測試用
  
  const loginUrl = `${cognitoDomain}/login?client_id=${clientId}&response_type=code&scope=email+openid+profile&redirect_uri=${redirectUri}`;
  
  // 導向 AWS 登入頁
  window.location.href = loginUrl;
}; -->