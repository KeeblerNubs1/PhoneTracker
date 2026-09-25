package com.example.phonetracker
import android.app.*
import android.content.Intent
import android.os.IBinder
import com.google.android.gms.location.*
import android.content.pm.PackageManager
import androidx.core.app.ActivityCompat
class LocationService:Service(){
 private lateinit var client:FusedLocationProviderClient
 override fun onCreate(){super.onCreate();val channel=NotificationChannel("tracker","Location Tracking",NotificationManager.IMPORTANCE_LOW);getSystemService(NotificationManager::class.java).createNotificationChannel(channel);startForeground(1,Notification.Builder(this,"tracker").setContentTitle("PhoneTracker").setContentText("Location tracking is active").setSmallIcon(android.R.drawable.ic_menu_mylocation).build());client=LocationServices.getFusedLocationProviderClient(this);if(ActivityCompat.checkSelfPermission(this,android.Manifest.permission.ACCESS_FINE_LOCATION)!=PackageManager.PERMISSION_GRANTED)return;val req=LocationRequest.Builder(Priority.PRIORITY_HIGH_ACCURACY,10000).setMinUpdateIntervalMillis(5000).build();client.requestLocationUpdates(req,callback,mainLooper)}
 private val callback=object:LocationCallback(){override fun onLocationResult(result:LocationResult){val p=getSharedPreferences("PhoneTracker",MODE_PRIVATE);val token=p.getString("deviceToken",null)?:return;val base=p.getString("apiUrl",null)?:return;val l=result.lastLocation?:return;Thread{Api.sendLocation(base,token,android.os.Build.MODEL,l.latitude,l.longitude,l.accuracy)}.start()}}
 override fun onDestroy(){client.removeLocationUpdates(callback);super.onDestroy()}
 override fun onBind(intent:Intent?):IBinder?=null
}
