export default function Login() {
  const handleGitHubLogin = () => {
    // Redirect to Supabase GitHub OAuth
    const supabaseUrl = import.meta.env.VITE_SUPABASE_URL;
    window.location.href = `${supabaseUrl}/auth/v1/authorize?provider=github`;
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="max-w-md w-full space-y-8 p-8">
        <div className="text-center">
          <h1 className="text-3xl font-bold text-gray-900">
            Code Review Agent
          </h1>
          <p className="mt-2 text-gray-600">
            AI-powered autonomous test generation
          </p>
        </div>
        <button
          onClick={handleGitHubLogin}
          className="w-full flex justify-center py-3 px-4 rounded-lg bg-gray-900 text-white font-medium hover:bg-gray-800 transition"
        >
          Sign in with GitHub
        </button>
      </div>
    </div>
  );
}
