package com.example.phonetracker

import android.Manifest
import android.content.Intent
import android.content.pm.PackageManager
import android.os.Bundle
import android.widget.*
import androidx.appcompat.app.AppCompatActivity
import androidx.core.app.ActivityCompat

class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        val box = LinearLayout(this).apply { orientation = LinearLayout.VERTICAL; setPadding(32,32,32,32) }
        val api = EditText(this).apply { hint = "API URL"; setText("http://192.168.1.50:5080") }
        val code = EditText(this).apply { hint = "6-digit pairing code" }
        val status = TextView(this).apply { text = "Not paired" }
        val pair = Button(this).apply { text = "Pair device" }
        val start = Button(this).apply { text = "Start tracking" }
        val stop = Button(this).apply { text = "Stop tracking" }
        box.addView(api); box.addView(code); box.addView(pair); box.addView(start); box.addView(stop); box.addView(status); setContentView(box)
        pair.setOnClickListener { Thread { val token = Api.pair(api.text.toString(), code.text.toString(), android.os.Build.MODEL); runOnUiThread { if (token != null) { getPreferences(0).edit().putString("deviceToken", token).putString("apiUrl", api.text.toString()).apply(); status.text="Paired" } else status.text="Pairing failed" } }.start() }
        start.setOnClickListener { if (ActivityCompat.checkSelfPermission(this, Manifest.permission.ACCESS_FINE_LOCATION) != PackageManager.PERMISSION_GRANTED) { ActivityCompat.requestPermissions(this, arrayOf(Manifest.permission.ACCESS_FINE_LOCATION, Manifest.permission.ACCESS_COARSE_LOCATION), 10); return@setOnClickListener }; startForegroundService(Intent(this, LocationService::class.java)); status.text="Tracking started" }
        stop.setOnClickListener { stopService(Intent(this, LocationService::class.java)); status.text="Tracking stopped" }
    }
}
