from features.coupling_miner import mine_logical_coupling

repo_path = r"C:\Users\HP\Desktop\Clone_PR\Architecture_modeling_system"

result = mine_logical_coupling(repo_path)

print("Commits analyzed:", result["commits_analyzed"])
print("Files analyzed:", result["files_analyzed"])

print("\nTop logical couplings:")

for coupling in result["couplings"][:10]:
    print(
        f"{coupling['file_a']} "
        f"<--> "
        f"{coupling['file_b']} | "
        f"Score: {coupling['coupling_score']}% | "
        f"Changed together: "
        f"{coupling['co_change_count']} times"
    )