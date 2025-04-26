import { createStore } from "vuex";
import auth from "./modules/auth";
import applications from "./modules/applications";

export default createStore({
  modules: {
    auth,
    applications,
  },
});
