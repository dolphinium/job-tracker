import { createStore } from "vuex";
import auth from "./modules/auth";
import applications from "./modules/applications";
import github from "./modules/github";

export default createStore({
  modules: {
    auth,
    applications,
    github,
  },
});
