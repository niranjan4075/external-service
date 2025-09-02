Got it 👍 — I’ve updated the **Implementation Plan** to include running the Aircard update queries during the release window. Here’s the revised CR draft:

---

## Change Request (CR) Document

**Change Summary**
Standardize Aircard descriptions for devices in the **standard user catalog** to clearly indicate whether Aircard capability is available or not.

**Scope**

* Applies only to devices under the **standard user catalog**.
* *Dell Pro 14 Plus Standard Windows* → Update description to **“Not aircard enabled.”**
* *Panasonic ToughBook FZ Rugged Windows* → Update description to **“Aircard enabled for field work.”**
* No impact to executive or special catalog devices.

**Impact**

* Users will be able to easily identify Aircard capability directly on the device card.
* Eliminates ambiguity and avoids dependency on external checks for Aircard status.
* Enhances user experience by providing consistent and clear descriptions during device selection.

**Justification / Benefits**

* Standardizes terminology across device catalog.
* Saves time for users during the ordering process.
* Prevents miscommunication and device selection errors.

**Testing / Validation**

* Verify that updated descriptions are correctly displayed on the device card UI.
* Validate with a sample set of standard users to confirm visibility and accuracy.
* Confirm no impact to executive or special catalog listings.

**Implementation Plan**

* Run Aircard update queries in the catalog database during the scheduled **release window**.
* Deploy updated metadata to the catalog system.
* Validate changes in non-production prior to release.
* Rollout to production after successful UAT confirmation.

---

Do you also want me to add a **Backout Plan** (e.g., revert queries to restore old descriptions) so this looks complete for CAB approval?
