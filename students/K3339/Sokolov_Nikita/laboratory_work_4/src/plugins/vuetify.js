import "@mdi/font/css/materialdesignicons.css"
import "vuetify/styles"
import { createVuetify } from "vuetify"
import * as components from "vuetify/components"
import * as directives from "vuetify/directives"

export default createVuetify({
  components,
  directives,
  theme: {
    defaultTheme: "clinic",
    themes: {
      clinic: {
        dark: false,
        colors: {
          primary: "#0B6E4F",
          secondary: "#1B4332",
          accent: "#95D5B2",
          surface: "#F7FBF8",
          background: "#EEF5F1",
          error: "#B00020",
        },
      },
    },
  },
})
