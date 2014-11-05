package com.example.zylocation;

import android.accounts.Account;
import android.accounts.AccountManager;
import android.app.Service;
import android.app.AlertDialog;
import android.content.Intent;
import android.location.Location;
import android.os.Bundle;
import android.os.IBinder;
import android.util.Log;

import com.google.android.gms.common.ConnectionResult;
import com.google.android.gms.common.GooglePlayServicesClient;
import com.google.android.gms.location.LocationRequest;
import com.google.android.gms.location.LocationClient;
import com.google.android.gms.location.LocationListener;

import java.io.BufferedInputStream;
import java.io.InputStream;
import java.io.IOException;
import java.lang.String;
import java.net.HttpURLConnection;
import java.net.URL;
import java.net.URLConnection;

public class ZYLocationService extends Service implements
		GooglePlayServicesClient.ConnectionCallbacks,
		GooglePlayServicesClient.OnConnectionFailedListener,
		LocationListener
{
    /** Called when the activity is first created. */
    @Override
    public int onStartCommand(Intent intent, int flags, int startId)
    {
		Log.d("ZYLOCATION", "onStartCommand");
		
		mLocationRequest = LocationRequest.create();
		mLocationRequest.setPriority(LocationRequest.PRIORITY_BALANCED_POWER_ACCURACY);
		mLocationRequest.setInterval(7 * 60 * 1000);  		 // 10 minutes
		mLocationRequest.setFastestInterval(3 * 60 * 1000);  // 5 minutes
		
		mLocationClient = new LocationClient(this, this, this);
        mLocationClient.connect();
		
		Log.d("ZYLOCATION", "started");
		
		return Service.START_STICKY;
    }
	
	@Override
	public IBinder onBind(Intent intent) {
		return null;
	}
	
	LocationRequest mLocationRequest;
    LocationClient mLocationClient;
	
	@Override
	public void onConnected(Bundle dataBundle) {
		// We are now connected to the location service, and can request location updates.
		mLocationClient.requestLocationUpdates(mLocationRequest, this);
		Log.d("zylocation", "Connected.");
	}
	
	@Override
	public void onDisconnected() {
		Log.w("zylocation", "Disconnected.");
		mLocationClient.connect();
	}
	
	@Override
	public void onConnectionFailed(ConnectionResult connectionResult) {
		Log.e("zylocation", "Connection failed.");
	}
	
	@Override
	public void onLocationChanged(Location location) {
		Log.d("ZYLOCATION", "onLocationChanged");
		final double lat = location.getLatitude();
		final double lng = location.getLongitude();
		final double accuracy = location.getAccuracy();
		
		// Get user's account name
		Account[] accounts = AccountManager.get(this).getAccountsByType("com.google");
		final String email;
		if (accounts.length == 0) {
			email = "UnknownUser";
		} else {
			email = accounts[0].name;
		}
		
		(new Thread() {
			public void run() {
				reportLocation(lat, lng, accuracy, email);
			}
		}).start();
	}
	
	private void reportLocation(double lat, double lng, double accuracy, String user_email) {
		Log.d("ZYLOCATION", "reportLocation");
		InputStream in = null;
		try {
			URL url = new URL("http://zylocation.appspot.com/report?lat=" + Double.toString(lat) +
				"&lng=" + Double.toString(lng) + "&accuracy=" + Double.toString(accuracy) +
				"&user_email=" + user_email);
    		HttpURLConnection urlConnection = (HttpURLConnection) url.openConnection();
		    in = new BufferedInputStream(urlConnection.getInputStream());
		} catch(IOException ex) {
		    Log.d("zylocation", ex.getMessage());
		} finally {
		    if (in != null) {
				try {
					in.close();
				} catch(IOException ex) {}
			}
		}
	}
}
