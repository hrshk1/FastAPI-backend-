# Understanding the Authentication Flow

In this application, we use **Google Authentication** to verify who you are before letting you manage the inventory. Here's a simple, step-by-step breakdown of how the whole process works between the frontend (the user interface you see) and the backend (the server handling data).

> [!NOTE]
> **A Note on OAuth Flows: Why a Token and not a Code?**
> If you've read about OAuth 2.0, you might know about the **Authorization Code Flow**, where the frontend gets a short-lived "code", sends it to the backend, and the backend securely trades that code with Google for tokens. 
> 
> However, this application uses a simpler, modern approach provided by Google Identity Services called the **Implicit Flow (specifically the Credential/ID Token flow)**. In this flow, Google directly gives the frontend an **ID Token** (a digitally signed JSON Web Token or JWT). The frontend then sends this ID Token directly to our backend. Since the ID Token is cryptographically signed by Google, our backend doesn't need to trade a code; it just mathematically verifies Google's signature to prove it's authentic.

## 1. The Frontend (React App)
This is where the user starts their journey.

### Step 1: Clicking the Login Button
When you open the app without being logged in, you see a "Sign in with Google" button. This button is powered by a library called `@react-oauth/google`.
- **Code:** [GoogleLogin component](file:///c:/Users/Harsh/Desktop/cd/fastapi/frontend/src/App.js#L245-L248)

### Step 2: Google gives us an ID Token
When you click that button and sign into your Google account, Google gives our frontend app a special digital "ID card" called an **ID Token**.
- **Code:** The successful login triggers the [`handleGoogleSuccess` function](file:///c:/Users/Harsh/Desktop/cd/fastapi/frontend/src/App.js#L198-L211). Inside this function, `credentialResponse.credential` is the ID Token Google gave us.

### Step 3: Sending the Token to our Backend
The frontend shouldn't just trust this token blindly. Instead, it immediately sends this token to our backend server to say, "Hey, this user just logged in with Google. Here's their ID card. Is it valid?"
- **Code:** This is done via an API request to the backend: [`api.post("/auth/google", { token })`](file:///c:/Users/Harsh/Desktop/cd/fastapi/frontend/src/App.js#L201).

### Step 4: Storing the Token
Once the backend says the token is valid, the frontend saves this token in its memory and in the browser's "Local Storage". This way, if you refresh the page, you don't have to log in again.
- **Code:** [`localStorage.setItem("authSession", ...)`](file:///c:/Users/Harsh/Desktop/cd/fastapi/frontend/src/App.js#L206).

### Step 5: Making Protected Requests
Now, every time the frontend asks the backend for data (like getting the list of products), it attaches this digital ID card (token) to the request header. This is like showing your pass to a security guard every time you enter a room.
- **Code:** The frontend creates an "Authorization" header that looks like `Bearer <your_token>`. This is handled by the [`authConfig` function](file:///c:/Users/Harsh/Desktop/cd/fastapi/frontend/src/App.js#L48-L55) which is attached to requests like [`api.get("/products", authConfig())`](file:///c:/Users/Harsh/Desktop/cd/fastapi/frontend/src/App.js#L62).

---

## 2. The Backend (FastAPI Server)
The backend acts as the bouncer for your data. It needs to make sure the tokens it receives are actually real and haven't been forged.

### Step 1: Receiving the Initial Login Token
When the frontend sends the ID Token to the backend for the first time (from Step 3 above), the backend receives it at the `/auth/google` endpoint.
- **Code:** [`google_auth` endpoint function](file:///c:/Users/Harsh/Desktop/cd/fastapi/main.py#L117-L120).

### Step 2: Asking Google, "Is this real?"
The backend takes the ID Token and verifies it with Google to ensure it's legitimate and hasn't been tampered with.
- **Code:** The backend calls the [`verify_google_token` function](file:///c:/Users/Harsh/Desktop/cd/fastapi/main.py#L44-L64).
- **How it works:** It makes a request to Google's special server: `https://oauth2.googleapis.com/tokeninfo?id_token=<token>`.

### Step 3: Checking the Details
Google responds with decoded information about the token. The backend checks two important things:
1. **Did Google issue this token for *our* app?** It checks if the "aud" (audience) matches our specific `GOOGLE_CLIENT_ID`. This prevents someone from using a token generated for a completely different app to access ours.
2. **Is the email verified?** It makes sure the user actually owns the email address.
- **Code:** These checks happen [here in the code](file:///c:/Users/Harsh/Desktop/cd/fastapi/main.py#L55-L58).

### Step 4: Securing the Data Endpoints
Once a user is authenticated, they can start requesting data (like viewing products). When the backend receives a request for products, it looks for that "Authorization" header (the digital ID card) the frontend sent.
- **Code:** Whenever the backend sees `user: GoogleUser = Depends(get_current_user)` in an endpoint (like [`get_products`](file:///c:/Users/Harsh/Desktop/cd/fastapi/main.py#L124-L127)), it forces the request to run through a security check.

### Step 5: The Security Check
The [`get_current_user` function](file:///c:/Users/Harsh/Desktop/cd/fastapi/main.py#L67-L70) extracts the token from the "Authorization" header (removing the word "Bearer "). It then runs that token back through the `verify_google_token` function from Step 2 to ensure it's still valid. If it's valid, the backend allows the request to continue and returns the products!
