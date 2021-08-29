export interface Guild {
    id: String;
    name: String;
    icon: String | null;
    owner: Boolean;
    permissions: Number;
    features: Array<String>;
    permissions_new: String;
}