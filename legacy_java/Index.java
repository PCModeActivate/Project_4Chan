import java.util.ArrayList;
import java.time.*; 
import java.io.*;
import java.io.File;
import java.io.IOException;
import java.util.Arrays;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Iterator;
import java.util.Scanner;
import java.lang.String;

public class Index{
    //Change arraylist to a more optimal data structure for deletion later
    HashMap<String, ArrayList<Image>> tagList = new HashMap<>();
    ArrayList<Image> imageList = new ArrayList<>();
    
    FileFilter imageFilter = new FileFilter() {
        //Override accept method
        public boolean accept(File file) {
                //if the file extension is image return true, else false
                if (file.getName().endsWith(".jpg") || file.getName().endsWith(".png") || file.getName().endsWith(".webp")) {
                    Image nImage = new Image (file.getName(), null);
                    //prompt here
                    assignTags(null, nImage);
                    imageList.add(nImage);
                    return true;
                }
                return false;
        }
    };

    File folder = new File("Repo-Chan");
    ArrayList<File> listOfFiles = new ArrayList<>(Arrays.asList(folder.listFiles(imageFilter)));//Checksum
    
    public void outputDirectory (){
        for (int i = 0; i < listOfFiles.size(); i++) {
            if (listOfFiles.get(i).isFile()) {
                System.out.println("File " + listOfFiles.get(i).getName());
            }
        }
    }
    // Need Query by name; Query by tag
    private class Image{
        String name;
        HashSet<String> tags = new HashSet<>();
        public Image (String name, HashSet<String> tags){
            this.name = name;
            this.tags = tags;
        }
        public String getName (){
            return name;
        }
        
        public HashSet<String> getTags (){
            return tags;
        }
        public String toString(){
            String outString = "";
            Iterator itr = tags.iterator(); 
            while (itr.hasNext()){
                outString += itr.hasNext() + " ";
            }
            return outString.substring(0,outString.length()-2);
        }
    }
    public void addImageToIndex(File folder){
        ArrayList<File> newList = new ArrayList<>(Arrays.asList(folder.listFiles(imageFilter)));
        listOfFiles.addAll(newList);
    }
    public void assignTags(HashSet<String> tags, Image im){
        ///Assumes that tags exist in tagList already; im is not necessarily tagged.
        im.tags.addAll(tags);
        Iterator itr = tags.iterator(); 
        while (itr.hasNext()){
            //Potential Optimization, not sorted
            tagList.get(itr.next()).add(im);
        }
    }
    public boolean isTag(String n){
        if (tagList.get(n) != null)
            return false;        
        else
            return tagList.containsKey(n);
    }
    public void addTag(String tag, ArrayList<Image> images){
        //Works only if tag does not exist and images is a list of images to add (or null if there is no images assigned)
        if (!isTag(tag)){
            for (int i = 0; i<images.size(); i++){
                images.get(i).tags.add(tag);
            }    
            tagList.put(tag, images);
        }
    }
    public void readTagFromSave(String tag, Image im){
        //Used for loading savefile only; adding to tagList only
        if (!isTag(tag)){
            tagList.get(tag).add(im);
        }
        else{
            ArrayList<Image> imgArrList = new ArrayList<>();
            imgArrList.add(im);
            tagList.put(tag, imgArrList);
        }
    }
    public void removeImage(Image img){ //O(n^2)
        imageList.remove(img); //remove(obj);
        Iterator itr = img.tags.iterator(); 
        while (itr.hasNext()){
            ArrayList<Image> arrayOfTag = tagList.get(itr.next());
            for (int k=0; k<arrayOfTag.size(); k++){
                if (arrayOfTag.get(k).equals(img)){
                    arrayOfTag.remove(k);
                }
            }
        }
    }
    public void removeImageString(String img){ //O(n^2)
        for (int i=0; i<imageList.size(); i++){
            if (imageList.get(i).name.equals(img)){
                imageList.remove(i);

                HashSet<String> tagsToRemove = imageList.get(i).getTags(); //Tags to edit                

                Iterator itr = tagsToRemove.iterator(); 
                while (itr.hasNext()){
                    ArrayList<Image> arrayOfTag = tagList.get(itr.next()); //Array of Images present in this tag   
                    for (int j=0; j<tagsToRemove.size(); j++){
                        for (int k=0; k<arrayOfTag.size(); k++){
                            if (arrayOfTag.get(k).getName().equals(img))
                                arrayOfTag.remove(k); //Remove img from this array
                        }
                    }            
                }
                break;
            }
        }
    }
    public void removeTag(String tag){ //O(n^2)
        ArrayList<Image> imgList = tagList.get(tag);
        tagList.remove(tag);
        for (int i=0; i<imgList.size(); i++){
            imgList.get(i).getTags().remove(tag); //remove(object)
        }
    }

    public void display (){
        //TBD; GUI Stuff
    }
    private boolean tagCompare(HashSet<String> tagA, HashSet<String> tagB){
        return tagA.containsAll(tagB);
    }
    public void queryByName (String input){
        for (int i = 0; i < imageList.size(); i++) {
            if (imageList.get(i).getName().toLowerCase().contains(input.toLowerCase())) {
                System.out.println(imageList.get(i).getName());
            }
        }
    }
    public void queryByTags (HashSet<String> tags){
        for (int i = 0; i < imageList.size(); i++) {
            if (tagCompare(tags,imageList.get(i).getTags()))
                System.out.println(imageList.get(i).getName());
        }
    }
    

    public void cache(){
        ///Null tags are not saved!!!
        String cache = "";
        for (int i=0; i<imageList.size(); i++){
            cache += imageList.get(i).getName() + ": " + imageList.get(i).toString();
        }
        try {
            FileWriter cacher = new FileWriter("Index.txt");
            cacher.write(cache);
            cacher.close();
        } 
        catch (IOException e) {
            System.out.println("An error occurred.");
            e.printStackTrace();
        }
    }
    public void readCache(){
        try {
            File cache = new File("Index.txt");
            Scanner reader = new Scanner(cache);
            while (reader.hasNextLine()) {
                String[] line = reader.nextLine().split(" ");
                if (line.length>1){
                    String[] tagArray = Arrays.copyOfRange(line, 1, line.length);
                    HashSet<String> tagSet = new HashSet<>(Arrays.asList(tagArray)); //Convert to hashset
                    
                    Image img = new Image(line[0], tagSet);
                    imageList.add(img); //Add to imagelist
                    
                    for (int i=1; i<line.length; i++)
                        readTagFromSave(line[i], img); //Add to tagList side
                }
                else{
                    imageList.add(new Image(line[0], null));
                }
            }
            reader.close();
          }
          catch (FileNotFoundException e) {
            System.out.println("An error occurred.");
            e.printStackTrace();
          }
    }
}