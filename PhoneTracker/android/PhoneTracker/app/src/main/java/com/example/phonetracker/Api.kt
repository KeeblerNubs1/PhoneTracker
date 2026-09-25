package com.example.phonetracker
import java.net.HttpURLConnection
import java.net.URL
import org.json.JSONObject
object Api {
 fun pair(base:String, code:String, deviceName:String):String?=try{val c=URL(base.trimEnd('/')+"/api/pair/complete").openConnection() as HttpURLConnection;c.requestMethod="POST";c.doOutput=true;c.setRequestProperty("Content-Type","application/json");c.outputStream.use{it.write(JSONObject().put("code",code).put("deviceName",deviceName).toString().toByteArray())};if(c.responseCode !in 200..299)null else JSONObject(c.inputStream.bufferedReader().readText()).getString("deviceToken")}catch(_:Exception){null}
 fun sendLocation(base:String,token:String,deviceId:String,lat:Double,lon:Double,accuracy:Float?){try{val c=URL(base.trimEnd('/')+"/api/location").openConnection() as HttpURLConnection;c.requestMethod="POST";c.doOutput=true;c.setRequestProperty("Content-Type","application/json");c.setRequestProperty("Authorization","Bearer $token");c.outputStream.use{it.write(JSONObject().put("deviceId",deviceId).put("latitude",lat).put("longitude",lon).put("accuracyMeters",accuracy).toString().toByteArray())};c.inputStream.close()}catch(_:Exception){}}
}
