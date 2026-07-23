package com.truthbuster.ai;

import android.annotation.SuppressLint;
import android.content.Intent;
import android.graphics.Bitmap;
import android.net.Uri;
import android.os.Bundle;
import android.view.KeyEvent;
import android.view.View;
import android.webkit.ValueCallback;
import android.webkit.WebChromeClient;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.widget.ProgressBar;
import android.widget.TextView;

import androidx.appcompat.app.AppCompatActivity;
import androidx.swiperefreshlayout.widget.SwipeRefreshLayout;

/**
 * Main Activity hosting the WebView that loads the Truth Buster AI web app.
 * Supports file uploads, pull-to-refresh, progress bar, and back navigation.
 */
public class MainActivity extends AppCompatActivity {

    // ═══════════════════════════════════════════════════
    // TODO: Replace this URL with your deployed Streamlit Cloud URL
    // Example: "https://truth-buster-ai.streamlit.app"
    // For local testing, use: "http://10.0.2.2:8501" (Android emulator)
    // ═══════════════════════════════════════════════════
    private static final String APP_URL = "https://truth-buster-ai.streamlit.app";

    private WebView webView;
    private ProgressBar progressBar;
    private SwipeRefreshLayout swipeRefresh;
    private TextView errorView;

    // File Upload support
    private ValueCallback<Uri[]> fileUploadCallback;
    private static final int FILE_CHOOSER_REQUEST = 1001;

    @SuppressLint("SetJavaScriptEnabled")
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        webView = findViewById(R.id.webview);
        progressBar = findViewById(R.id.progress_bar);
        swipeRefresh = findViewById(R.id.swipe_refresh);
        errorView = findViewById(R.id.error_view);

        // ─── WebView Settings ───
        WebSettings settings = webView.getSettings();
        settings.setJavaScriptEnabled(true);
        settings.setDomStorageEnabled(true);
        settings.setAllowFileAccess(true);
        settings.setAllowContentAccess(true);
        settings.setLoadWithOverviewMode(true);
        settings.setUseWideViewPort(true);
        settings.setSupportZoom(false);
        settings.setBuiltInZoomControls(false);
        settings.setMixedContentMode(WebSettings.MIXED_CONTENT_ALWAYS_ALLOW);
        settings.setCacheMode(WebSettings.LOAD_DEFAULT);
        settings.setMediaPlaybackRequiresUserGesture(false);

        // User agent to identify as mobile browser
        String userAgent = settings.getUserAgentString();
        settings.setUserAgentString(userAgent + " TruthBusterAI/2.0");

        // ─── WebViewClient (page load handling) ───
        webView.setWebViewClient(new WebViewClient() {
            @Override
            public void onPageStarted(WebView view, String url, Bitmap favicon) {
                progressBar.setVisibility(View.VISIBLE);
                errorView.setVisibility(View.GONE);
                webView.setVisibility(View.VISIBLE);
            }

            @Override
            public void onPageFinished(WebView view, String url) {
                progressBar.setVisibility(View.GONE);
                swipeRefresh.setRefreshing(false);

                // Inject CSS to force mobile-friendly rendering
                String mobileCSS = "javascript:(function(){" +
                    "var style=document.createElement('style');" +
                    "style.innerHTML='" +
                    "body{-webkit-text-size-adjust:100%} " +
                    "[data-testid=\"stSidebar\"]{display:none !important} " +
                    ".main .block-container{padding:1rem 0.8rem !important; max-width:100% !important} " +
                    "h1{font-size:1.6rem !important} " +
                    "';" +
                    "document.head.appendChild(style);" +
                    "})()";
                view.loadUrl(mobileCSS);
            }

            @Override
            public void onReceivedError(WebView view, int errorCode, String description, String failingUrl) {
                webView.setVisibility(View.GONE);
                progressBar.setVisibility(View.GONE);
                errorView.setVisibility(View.VISIBLE);
                errorView.setText("⚠️ Unable to connect\n\nPlease check your internet connection and try again.\n\nTap to retry.");
                errorView.setOnClickListener(v -> {
                    errorView.setVisibility(View.GONE);
                    webView.setVisibility(View.VISIBLE);
                    webView.loadUrl(APP_URL);
                });
            }

            @Override
            public boolean shouldOverrideUrlLoading(WebView view, String url) {
                // Open external links in browser, keep internal URLs in WebView
                if (url.contains("truth-buster") || url.contains("streamlit") || url.contains("localhost")) {
                    return false;
                }
                Intent intent = new Intent(Intent.ACTION_VIEW, Uri.parse(url));
                startActivity(intent);
                return true;
            }
        });

        // ─── WebChromeClient (file uploads & progress) ───
        webView.setWebChromeClient(new WebChromeClient() {
            @Override
            public void onProgressChanged(WebView view, int newProgress) {
                progressBar.setProgress(newProgress);
                if (newProgress == 100) {
                    progressBar.setVisibility(View.GONE);
                }
            }

            // Handle file uploads (for image evidence upload)
            @Override
            public boolean onShowFileChooser(WebView webView, ValueCallback<Uri[]> filePathCallback, FileChooserParams fileChooserParams) {
                if (fileUploadCallback != null) {
                    fileUploadCallback.onReceiveValue(null);
                }
                fileUploadCallback = filePathCallback;

                Intent intent = fileChooserParams.createIntent();
                try {
                    startActivityForResult(intent, FILE_CHOOSER_REQUEST);
                } catch (Exception e) {
                    fileUploadCallback = null;
                    return false;
                }
                return true;
            }
        });

        // ─── Pull-to-Refresh ───
        swipeRefresh.setColorSchemeColors(0xFFEF4444, 0xFF6366F1, 0xFF22C55E);
        swipeRefresh.setProgressBackgroundColorSchemeColor(0xFF11141D);
        swipeRefresh.setOnRefreshListener(() -> webView.reload());

        // Load the app
        webView.loadUrl(APP_URL);
    }

    // ─── Handle File Upload Result ───
    @Override
    protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        super.onActivityResult(requestCode, resultCode, data);
        if (requestCode == FILE_CHOOSER_REQUEST) {
            if (fileUploadCallback != null) {
                Uri[] results = null;
                if (resultCode == RESULT_OK && data != null) {
                    String dataString = data.getDataString();
                    if (dataString != null) {
                        results = new Uri[]{Uri.parse(dataString)};
                    }
                }
                fileUploadCallback.onReceiveValue(results);
                fileUploadCallback = null;
            }
        }
    }

    // ─── Handle Back Button (navigate back in WebView history) ───
    @Override
    public boolean onKeyDown(int keyCode, KeyEvent event) {
        if (keyCode == KeyEvent.KEYCODE_BACK && webView.canGoBack()) {
            webView.goBack();
            return true;
        }
        return super.onKeyDown(keyCode, event);
    }
}
