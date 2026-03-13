package br.com.x1co.wdp

import android.content.Context
import android.graphics.Color
import android.graphics.Typeface
import android.view.Gravity
import android.widget.ImageView
import android.widget.LinearLayout
import android.widget.TextView
import com.bumptech.glide.Glide

class EasyWdlRenderer(
    private val context: Context, 
    private val container: LinearLayout,
    private val onNavigate: (String) -> Unit
) {
    private val inputs = mutableMapOf<String, android.widget.EditText>()

    fun render(content: String) {
        container.removeAllViews()
        inputs.clear()
        
        val tagRegex = "\\(.*?\\)".toRegex()
        val tags = tagRegex.findAll(content).toList()
        val plainTexts = content.split(tagRegex)
        
        val combined = mutableListOf<String>()
        for (i in plainTexts.indices) {
            if (plainTexts[i].isNotEmpty()) combined.add(plainTexts[i])
            if (i < tags.size) combined.add(tags[i].value)
        }

        var currentTag: String? = null
        var currentLinkUrl: String? = null
        
        for (token in combined) {
            if (token.startsWith("(") && token.endsWith(")")) {
                val tagContent = token.substring(1, token.length - 1)
                val tagName = tagContent.lowercase().split(":")[0]
                
                if (tagName == currentTag) {
                    currentTag = null
                    currentLinkUrl = null
                    continue
                }
                
                when (tagName) {
                    "input" -> {
                        addInput(tagContent.substringAfter(":"))
                        currentTag = null
                    }
                    "button" -> {
                        addButton(tagContent.substringAfter(":"))
                        currentTag = null
                    }
                    "link" -> {
                        currentTag = "link"
                        currentLinkUrl = if (tagContent.contains(":")) tagContent.substringAfter(":") else null
                    }
                    else -> currentTag = tagName
                }
            } else {
                val text = token.trim()
                if (text.isEmpty()) continue

                when (currentTag) {
                    "title" -> addTextView(text, 26f, true, true)
                    "text" -> addTextView(text, 16f, false, false)
                    "center" -> addTextView(text, 16f, false, true)
                    "image" -> addImageView(text)
                    "link" -> addTextView(text, 16f, true, false, Color.BLUE, currentLinkUrl)
                    "input" -> addInput(text)
                    "button" -> addButton(text)
                    else -> addTextView(text, 16f, false, false)
                }
            }
        }
    }

    private fun addInput(spec: String) {
        val varname = if (spec.contains(":")) spec.substringBefore(":") else spec
        val placeholder = if (spec.contains(":")) spec.substringAfter(":") else ""
        
        val et = android.widget.EditText(context).apply {
            hint = placeholder
            layoutParams = LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT,
                LinearLayout.LayoutParams.WRAP_CONTENT
            ).apply { setMargins(20, 10, 20, 10) }
        }
        inputs[varname] = et
        container.addView(et)
    }

    private fun addButton(spec: String) {
        val actionUrl = if (spec.contains(":")) spec.substringBeforeLast(":") else spec
        val label = if (spec.contains(":")) spec.substringAfterLast(":") else "Submit"
        
        val btn = android.widget.Button(context).apply {
            text = label
            setOnClickListener {
                submitForm(actionUrl)
            }
            layoutParams = LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.WRAP_CONTENT,
                LinearLayout.LayoutParams.WRAP_CONTENT
            ).apply { 
                gravity = Gravity.CENTER_HORIZONTAL
                setMargins(0, 20, 0, 20)
            }
        }
        container.addView(btn)
    }

    private fun submitForm(actionUrl: String) {
        val params = inputs.map { (k, v) -> "$k=${java.net.URLEncoder.encode(v.text.toString(), "UTF-8")}" }
        val query = params.joinToString("&")
        val finalUrl = if (actionUrl.contains("?")) "$actionUrl&$query" else "$actionUrl?$query"
        onNavigate(finalUrl)
    }

    private fun addTextView(text: String, size: Float, bold: Boolean, center: Boolean, color: Int = Color.BLACK, linkUrl: String? = null) {
        val tv = TextView(context).apply {
            this.text = text
            this.textSize = size
            this.setTextColor(color)
            if (bold) setTypeface(null, Typeface.BOLD)
            if (center) gravity = Gravity.CENTER_HORIZONTAL
            setPadding(0, 12, 0, 12)
            
            if (linkUrl != null) {
                setOnClickListener { onNavigate(linkUrl) }
            }
        }
        container.addView(tv)
    }

    private fun addImageView(url: String) {
        if (!url.startsWith("http")) return
        val iv = ImageView(context).apply {
            layoutParams = LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT,
                LinearLayout.LayoutParams.WRAP_CONTENT
            ).apply { setMargins(0, 20, 0, 20) }
            adjustViewBounds = true
        }
        Glide.with(context).load(url).into(iv)
        container.addView(iv)
    }
}
