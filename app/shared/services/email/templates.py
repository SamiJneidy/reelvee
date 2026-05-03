"""
HTML email templates.

All templates use inline CSS for maximum email-client compatibility.
Color palette:
  primary   #4F46E5  (indigo-600)
  text      #111827  (gray-900)
  muted     #6B7280  (gray-500)
  bg        #F3F4F6  (gray-100)
  card      #FFFFFF
  border    #E5E7EB  (gray-200)
"""

_BRAND = "Reelvee"
_BRAND_COLOR = "#4F46E5"
_FONT = "font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif"


def _base(title: str, preview: str, body_html: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width,initial-scale=1"/>
  <title>{title}</title>
  <!--[if mso]><noscript><xml><o:OfficeDocumentSettings><o:PixelsPerInch>96</o:PixelsPerInch></o:OfficeDocumentSettings></xml></noscript><![endif]-->
</head>
<body style="margin:0;padding:0;background:#F3F4F6;{_FONT}">
  <!-- preview text (hidden) -->
  <div style="display:none;max-height:0;overflow:hidden;mso-hide:all">{preview}&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;‌&nbsp;‌</div>

  <table width="100%" cellpadding="0" cellspacing="0" border="0" style="background:#F3F4F6">
    <tr>
      <td align="center" style="padding:40px 16px">

        <!-- Card -->
        <table width="100%" cellpadding="0" cellspacing="0" border="0"
               style="max-width:560px;background:#FFFFFF;border-radius:12px;border:1px solid #E5E7EB;overflow:hidden">

          <!-- Header -->
          <tr>
            <td style="background:{_BRAND_COLOR};padding:28px 40px">
              <p style="margin:0;{_FONT};font-size:22px;font-weight:700;color:#FFFFFF;letter-spacing:-0.3px">
                {_BRAND}
              </p>
            </td>
          </tr>

          <!-- Body -->
          <tr>
            <td style="padding:36px 40px 28px">
              {body_html}
            </td>
          </tr>

          <!-- Footer -->
          <tr>
            <td style="background:#F9FAFB;border-top:1px solid #E5E7EB;padding:20px 40px">
              <p style="margin:0;{_FONT};font-size:12px;color:#9CA3AF;line-height:1.6">
                You received this email because an action was performed on your {_BRAND} account.
                If this wasn't you, you can safely ignore this email.
              </p>
              <p style="margin:8px 0 0;{_FONT};font-size:12px;color:#9CA3AF">
                &copy; {_BRAND} &mdash; All rights reserved.
              </p>
            </td>
          </tr>

        </table>
        <!-- /Card -->

      </td>
    </tr>
  </table>
</body>
</html>"""


# ---------------------------------------------------------------------------
# Button helper
# ---------------------------------------------------------------------------

def _button(label: str, href: str) -> str:
    return f"""
<table cellpadding="0" cellspacing="0" border="0" style="margin:28px 0 0">
  <tr>
    <td style="border-radius:8px;background:{_BRAND_COLOR}">
      <a href="{href}"
         style="display:inline-block;padding:13px 28px;{_FONT};font-size:15px;font-weight:600;
                color:#FFFFFF;text-decoration:none;border-radius:8px">
        {label}
      </a>
    </td>
  </tr>
</table>"""


# ---------------------------------------------------------------------------
# Text helpers
# ---------------------------------------------------------------------------

def _h1(text: str) -> str:
    return f'<h1 style="margin:0 0 8px;{_FONT};font-size:22px;font-weight:700;color:#111827;letter-spacing:-0.3px">{text}</h1>'

def _p(text: str, color: str = "#374151", size: str = "15px") -> str:
    return f'<p style="margin:12px 0 0;{_FONT};font-size:{size};color:{color};line-height:1.65">{text}</p>'

def _divider() -> str:
    return '<hr style="border:none;border-top:1px solid #E5E7EB;margin:28px 0"/>'


# ---------------------------------------------------------------------------
# Welcome (post-signup, before email verification / onboarding completion)
# ---------------------------------------------------------------------------

def welcome_template(email: str) -> str:
    body = (
        _h1(f"Thanks for joining {_BRAND}")
        + _p(
            f"We created an account for <strong>{email}</strong>. "
            "You should also receive a <strong>separate email</strong> with a one-time code "
            "to verify this address."
        )
        + _p(
            "After you verify your email, you will finish setting up your profile and store "
            "in the app. Your store is not live until you complete that step."
        )
        + _divider()
        + _p(
            "With Reelvee you can:<br/>"
            "• Create and manage your product catalog<br/>"
            "• Receive and track orders in real time<br/>"
            "• Share your store link with customers instantly",
            color="#6B7280",
            size="14px",
        )
        + _p(
            "If you didn't create this account, please ignore this email.",
            color="#9CA3AF",
            size="13px",
        )
    )
    return _base(
        title=f"Welcome to {_BRAND}",
        preview=f"Next: verify your email to continue with {_BRAND}",
        body_html=body,
    )


# ---------------------------------------------------------------------------
# Onboarding complete (after signup / profile + store creation)
# ---------------------------------------------------------------------------

def onboarding_template(
    email: str,
    first_name: str | None,
    store_public_url: str,
) -> str:
    name = (first_name or "").strip()
    salutation = f"Hi <strong>{name}</strong>," if name else f"Hi <strong>{email}</strong>,"
    body = (
        _h1("You are all set")
        + _p(salutation)
        + _p(
            "Your profile and store are saved. Customers can visit your public page using the link below."
        )
        + _button("View your store", store_public_url)
        + _divider()
        + _p(
            "Next steps: add products, customize your page, and share your link. "
            f"If you need anything, we are here to help.",
            color="#6B7280",
            size="14px",
        )
        + _p(
            f'Or open this link:<br/>'
            f'<a href="{store_public_url}" style="color:{_BRAND_COLOR};word-break:break-all">'
            f"{store_public_url}</a>",
            color="#6B7280",
            size="13px",
        )
        + _p(
            f"If you did not finish onboarding on {_BRAND}, contact support.",
            color="#9CA3AF",
            size="13px",
        )
    )
    return _base(
        title=f"Your {_BRAND} store is ready",
        preview="Your store page is live — open it here",
        body_html=body,
    )


# ---------------------------------------------------------------------------
# Email verification OTP
# ---------------------------------------------------------------------------

def email_verification_otp_template(code: str) -> str:
    otp_block = f"""
<table cellpadding="0" cellspacing="0" border="0" style="margin:24px 0 0">
  <tr>
    <td style="background:#EEF2FF;border:1.5px dashed {_BRAND_COLOR};
               border-radius:10px;padding:18px 40px;text-align:center">
      <p style="margin:0;{_FONT};font-size:36px;font-weight:800;
                letter-spacing:10px;color:{_BRAND_COLOR}">{code}</p>
    </td>
  </tr>
</table>"""

    body = (
        _h1("Verify your email address")
        + _p("Use the one-time code below to verify your email. The code expires in a few minutes.")
        + otp_block
        + _divider()
        + _p(
            f"Never share this code with anyone, including {_BRAND} support.",
            color="#9CA3AF",
            size="13px",
        )
    )
    return _base(
        title="Verify your email",
        preview=f"Your verification code is {code}",
        body_html=body,
    )


# ---------------------------------------------------------------------------
# Password reset
# ---------------------------------------------------------------------------

def password_reset_template(link: str) -> str:
    body = (
        _h1("Reset your password")
        + _p(
            "We received a request to reset the password for your account. "
            "Click the button below to choose a new password."
        )
        + _button("Reset Password", link)
        + _divider()
        + _p(
            f'Or copy and paste this link into your browser:<br/>'
            f'<a href="{link}" style="color:{_BRAND_COLOR};word-break:break-all">{link}</a>',
            color="#6B7280",
            size="13px",
        )
        + _p(
            "This link will expire soon. If you didn't request a password reset, "
            "you can safely ignore this email — your password won't change.",
            color="#9CA3AF",
            size="13px",
        )
    )
    return _base(
        title="Reset your password",
        preview=f"Reset your {_BRAND} password",
        body_html=body,
    )


# ---------------------------------------------------------------------------
# Email change confirmation
# ---------------------------------------------------------------------------

def email_change_template(link: str) -> str:
    body = (
        _h1("Confirm your new email address")
        + _p(
            "You recently requested to change the email address on your account. "
            "Click the button below to confirm and complete the change."
        )
        + _button("Confirm Email Change", link)
        + _divider()
        + _p(
            f'Or copy and paste this link into your browser:<br/>'
            f'<a href="{link}" style="color:{_BRAND_COLOR};word-break:break-all">{link}</a>',
            color="#6B7280",
            size="13px",
        )
        + _p(
            "If you didn't request this change, please ignore this email. "
            "Your current email address will remain active.",
            color="#9CA3AF",
            size="13px",
        )
    )
    return _base(
        title="Confirm your email change",
        preview=f"Confirm your new email address for {_BRAND}",
        body_html=body,
    )
