package br.com.x1co.wdp

import android.os.Bundle
import android.widget.Button
import android.widget.EditText
import android.widget.LinearLayout
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity

class MainActivity : AppCompatActivity() {
    private lateinit var urlInput: EditText
    private lateinit var contentContainer: LinearLayout
    private lateinit var renderer: EasyWdlRenderer
    private val client = WdpClient()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        urlInput = findViewById(R.id.urlInput)
        contentContainer = findViewById(R.id.contentContainer)
        renderer = EasyWdlRenderer(this, contentContainer) { newUrl ->
            urlInput.setText(newUrl)
            fetchContent(newUrl)
        }

        findViewById<Button>(R.id.goButton).setOnClickListener {
            val url = urlInput.text.toString().trim()
            if (url.isNotEmpty()) {
                fetchContent(url)
            } else {
                // If URL input is empty, set default and fetch
                urlInput.setText("wdp://x1co.com.br:5555")
                fetchContent("wdp://x1co.com.br:5555")
            }
        }
        
        // Load default content
        fetchContent("wdp://x1co.com.br:5555")
    }

    private fun fetchContent(url: String) {
        client.fetch(url) { result ->
            runOnUiThread {
                result.onSuccess { content ->
                    renderer.render(content)
                }.onFailure { error ->
                    val errorMsg = error.toString()
                    Toast.makeText(this, "Error: $errorMsg", Toast.LENGTH_LONG).show()
                    renderer.render("(text) Error loading page: $errorMsg (text)")
                }
            }
        }
    }
}
