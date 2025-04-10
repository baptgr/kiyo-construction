import NextAuth from "next-auth";
import Google from "next-auth/providers/google";

export const { handlers, auth, signIn, signOut } = NextAuth({
  providers: [
    Google({
      clientId: process.env.GOOGLE_CLIENT_ID,
      clientSecret: process.env.GOOGLE_CLIENT_SECRET,
      authorization: {
        params: {
          scope: "https://www.googleapis.com/auth/userinfo.profile https://www.googleapis.com/auth/userinfo.email https://www.googleapis.com/auth/spreadsheets https://www.googleapis.com/auth/drive.file",
          access_type: "offline",
          prompt: "consent"
        }
      }
    }),
  ],
  callbacks: {
    async jwt({ token, account, user }) {
      // Initial sign in
      if (account && user) {
        // DEBUG: Log details when a user initially signs in and account info is received.
        // console.log("Initial sign in - Account info received:", {
        //   accessToken: !!account.access_token,
        //   refreshToken: !!account.refresh_token,
        //   expiresAt: account.expires_at
        // });
        return {
          accessToken: account.access_token,
          accessTokenExpires: Date.now() + account.expires_in * 1000,
          refreshToken: account.refresh_token,
          user,
        };
      }

      // Return previous token if the access token has not expired yet
      if (Date.now() < token.accessTokenExpires) {
        // DEBUG: Log that the current access token is still valid.
        // console.log("Token still valid", { expiresAt: token.accessTokenExpires, now: Date.now() });
        return token;
      }

      // Access token has expired, try to update it
      // DEBUG: Log that the access token has expired and a refresh attempt is being made.
      // console.log("Access token expired, attempting refresh...");
      return refreshAccessToken(token);
    },
    async session({ session, token }) {
      // Send properties to the client, like an access_token and user id from the token object.
      session.user = token.user;
      session.accessToken = token.accessToken;
      session.error = token.error;
      // DEBUG: Log session details including token presence and any errors.
      // console.log("Session callback", { hasAccessToken: !!session.accessToken, error: session.error });
      return session;
    },
  },
  debug: true, // Enable debug messages
});

async function refreshAccessToken(token) {
  try {
    const url = "https://oauth2.googleapis.com/token";
    const response = await fetch(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
      },
      body: new URLSearchParams({
        client_id: process.env.GOOGLE_CLIENT_ID,
        client_secret: process.env.GOOGLE_CLIENT_SECRET,
        grant_type: "refresh_token",
        refresh_token: token.refreshToken,
      }),
    });

    const refreshedTokens = await response.json();

    if (!response.ok) {
      // DEBUG: Log error details if the token refresh request failed.
      // console.error("Error refreshing token:", refreshedTokens);
      throw refreshedTokens;
    }

    // DEBUG: Log confirmation of successful token refresh.
    // console.log("Tokens refreshed successfully");

    return {
      ...token, // Keep the existing token properties
      accessToken: refreshedTokens.access_token,
      accessTokenExpires: Date.now() + refreshedTokens.expires_in * 1000,
      // Fallback refreshToken check: Google might not always return a new refresh token
      refreshToken: refreshedTokens.refresh_token ?? token.refreshToken, 
    };
  } catch (error) {
    // DEBUG: Log any errors caught during the access token refresh process.
    // console.error("Error refreshing access token", error);
    // Indicate error and potentially invalidate session
    return {
      ...token,
      error: "RefreshAccessTokenError",
    };
  }
} 