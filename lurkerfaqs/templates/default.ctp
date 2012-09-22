<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
"http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">


<head>

	<title><?php echo $title_for_layout?></title>
	
	<!--<link rel="shortcut icon" href="/cake/favicon.ico" /> -->
	
	<!--  <link rel="shortcut icon" href="favicon.ico" type="image/x-icon"> -->
	
	
	<?php echo $this->Html->css('default') ?>
	<!-- Include external files and scripts here (See HTML helper for more info.) -->
	<?php echo $scripts_for_layout ?>
	
	<script type="text/javascript">
	
	  var _gaq = _gaq || [];
	  _gaq.push(['_setAccount', 'UA-22160565-1']);
	  _gaq.push(['_trackPageview']);
	
	  (function() {
	    var ga = document.createElement('script'); ga.type = 'text/javascript'; ga.async = true;
	    ga.src = ('https:' == document.location.protocol ? 'https://ssl' : 'http://www') + '.google-analytics.com/ga.js';
	    var s = document.getElementsByTagName('script')[0]; s.parentNode.insertBefore(ga, s);
	  })();
	
	</script>	
</head>

<body>

<div id="container">
<!-- If you'd like some sort of menu to  show up on all of your views, include it here -->
<div id="header">
    <div id="headerBlock">
    	<div id="logo" class="center">
	    	<a href="http://www.lurkerfaqs.com">
	    		<?php echo('<img style="border: 0" src="'. $this->webroot . 'img/lurkerlogo.jpg" />'); ?>
	    	</a>
    	</div>
    </div>

    <div id="menu">
    	<div class="menuWrapper blockCenter">


            <?php
                    echo("<div class='block'>");
                    echo(
                                    $this->Html->link(
                                            "Boards",
                                            array(
                                                    'controller' => 'boards',
                                                    'action' => 'index'
                                            )
                                    )
                    );
                    echo("</div>");

                    echo("<div class='block'>");
                    echo( $this->Html->link(
                            "Top Users",
                            array(
                                'controller' => 'users',
                                'action' => 'topUsers'
                            )
                        )
                    );
                    echo("</div>");

                    /*echo(
                                    $this->Html->link(
                                            "User Search",
                                            array(
                                                    'controller' => 'pages',
                                                    'action' => 'userSearch'
                                            )
                                    )
                    );*/
                    echo("<div class='block'>");
                    echo(
                                    $this->Html->link(
                                            "FAQ",
                                            array(
                                                    'controller' => 'pages',
                                                    'action' => 'faq'
                                            )
                                    )
                    );
                    echo("</div>");
            ?>

            <div class="searchbar right">
                    <?php
                           echo(
                                    $this->Form->create('User',
                                                    array(
                                                            'type' => 'get',
                                                            'action' => 'searchPost'
                                                    )
                                    )
                            );

                            $userSearchLink =   $this->Html->link(
                                                        "Username",
                                                        array(
                                                                'controller' => 'pages',
                                                                'action' => 'user_search'
                                                        )
                                                );
                            echo $this->Form->input('search_text', array('type' => 'text', 'label' => $userSearchLink  ));
                            //echo("<div class='submit left'><input type='submit' value='Search' /></div> <div class='clear'></div> </form> ")
                            echo( $this->Form->end('Search'));
                    ?>
            </div>

            <div class='clear'></div>
    	</div>
    
    </div>
    <div class="headerHorizRule"></div>
</div>



<div id="contents">
<!-- Here's where I want my views to be displayed -->
<?php echo $content_for_layout ?>
</div>



<br/><br/><br/><br/><br/>
<!-- Add a footer to each displayed page --> 
<div id="footer">
	<div id="footerBar" class="blockCenter">
	<div id="footerLinks" class="innerCenter">
				<?php 
					echo("Other Resources: ");
					echo("<a href='http://www.gamefaqs.com'>GameFAQs</a>");
					echo("<a href='http://wikicedia.net/'>WikiCEdia</a>");
					echo("<a href='http://www.gamefaqsarchive.com/'>GameFAQs Archive</a>");
				?>  	
	</div>
	</div>
</div>
</div>


</body>
</html>
