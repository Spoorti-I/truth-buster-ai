package com.truthbuster.ai;

import android.content.Intent;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.view.animation.AlphaAnimation;
import android.view.animation.Animation;
import android.widget.ImageView;
import android.widget.TextView;
import androidx.appcompat.app.AppCompatActivity;

/**
 * Animated Splash Screen with fade-in branding
 */
public class SplashActivity extends AppCompatActivity {

    private static final int SPLASH_DELAY = 2200;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_splash);

        // Fade-in animation for logo + title
        TextView appTitle = findViewById(R.id.splash_title);
        TextView appTagline = findViewById(R.id.splash_tagline);
        TextView appEmoji = findViewById(R.id.splash_emoji);

        AlphaAnimation fadeIn = new AlphaAnimation(0.0f, 1.0f);
        fadeIn.setDuration(1200);
        fadeIn.setFillAfter(true);

        AlphaAnimation fadeInSlow = new AlphaAnimation(0.0f, 1.0f);
        fadeInSlow.setDuration(1800);
        fadeInSlow.setStartOffset(400);
        fadeInSlow.setFillAfter(true);

        appEmoji.startAnimation(fadeIn);
        appTitle.startAnimation(fadeIn);
        appTagline.startAnimation(fadeInSlow);

        // Navigate to main screen after delay
        new Handler(Looper.getMainLooper()).postDelayed(() -> {
            Intent intent = new Intent(SplashActivity.this, MainActivity.class);
            startActivity(intent);
            overridePendingTransition(android.R.anim.fade_in, android.R.anim.fade_out);
            finish();
        }, SPLASH_DELAY);
    }
}
