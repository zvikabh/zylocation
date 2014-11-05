package com.example.zylocation;

import android.accounts.Account;
import android.accounts.AccountManager;
import android.app.Activity;
import android.app.AlertDialog;
import android.location.Location;
import android.os.Bundle;
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

public class MainActivity extends Activity
{
    /** Called when the activity is first created. */
    @Override
    public void onCreate(Bundle savedInstanceState)
    {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.main);
		
		Log.d("ZYLOCATION", "MainActivity.onCreate");
		
		/*mLocationRequest = LocationRequest.create();
		mLocationRequest.setPriority(LocationRequest.PRIORITY_BALANCED_POWER_ACCURACY);
		mLocationRequest.setInterval(1 * 60 * 1000);  // 1 minute
		mLocationRequest.setFastestInterval(30 * 1000);  // 30 seconds
		
		mLocationClient = new LocationClient(this, this, this);*/
		
		messageBox("hello");
    }
	
    @Override
    protected void onStart() {
		super.onStart();
        //mLocationClient.connect();
    }

	/*LocationRequest mLocationRequest;
    LocationClient mLocationClient;*/
	
	private void messageBox(String message) {
        AlertDialog.Builder dlgAlert  = new AlertDialog.Builder(this);                      
	    dlgAlert.setMessage(message);
		dlgAlert.setTitle("ZY Location");
		dlgAlert.setPositiveButton("OK", null);
		dlgAlert.setCancelable(true);
		dlgAlert.create().show();
	}
}
